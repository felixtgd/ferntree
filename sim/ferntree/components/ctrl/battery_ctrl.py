import numpy as np
import cvxpy as cp

from components.dev import device

import logging

logger = logging.getLogger("ferntree")


class BatteryCtrl(device.Device):
    def __init__(self, host, ctrl_specs, smart_meter) -> None:
        """Initializes a new instance of the BatteryCtrl class."""

        super().__init__(host)

        # Planning horizon for battery operation [days]: set to timesteps per planning horizon
        self.planning_horizon = int(
            ctrl_specs.get("planning_horizon", 1) * 24 * 60 * 60 / self.host.timebase
        )
        # Useable capacity [0 ... 1]: safety margins for battery operation
        self.useable_capacity = ctrl_specs.get("useable_capacity", 0.8)
        # Use greedy strategy or valley filling method as control strategy
        self.greedy = ctrl_specs.get("greedy", False)
        # Use optimisation to determine fill levels
        self.opt_fill = ctrl_specs.get("opt_fill", False)

        # Smart meter object to get net load of house
        self.smart_meter = smart_meter

        # Predcition of net load power profile P_net_load of house
        self.prediction_window = self.planning_horizon
        self.P_load_pred = np.zeros(self.prediction_window)

        # Initialise fill levels (greedy strategy as default)
        self.Z_charge = 0.0
        self.Z_discharge = 0.0

    def set_battery_power(self, soc_t, bat_max_pwr, bat_cap):
        # Get current net load of house
        p_t = self.smart_meter.get_net_load()
        # Update prediction of net load power profile
        self.P_load_pred = self.update_prediction(self.P_load_pred, p_t)

        # If not greedy and start of new day/planning horizon, update Z values
        if not self.greedy and self.host.current_timestep % self.planning_horizon == 0:
            # Update fill levels based on predicted net load of house
            self.Z_charge, self.Z_discharge = self.set_fill_levels(self.P_load_pred)

        # Determine battery power using Z values
        bat_pwr, soc_t, Z_t = self.fill_level_battery_power(
            self.Z_charge, self.Z_discharge, p_t, soc_t, bat_max_pwr, bat_cap
        )

        return bat_pwr, soc_t, Z_t, self.P_load_pred[0]

    def update_prediction(self, P_pred, p_t):
        """Update prediction window for optimisation
        - Update prediction at current timestep with actual net load value
        - Shift prediction window by one timestep

        Args:
            P_pred (numpy.ndarray): Array with predicted power values.
            p_t (float): Net load of the house at current timestep.
        """
        update_factor = (
            0.2  # update factor/weight for current value in prediction window
        )

        # Update: Take weighted average of current value and prediction
        p_updated = update_factor * p_t + (1 - update_factor) * P_pred[0]
        # Shift prediction window: Set first element to end of array
        P_pred[:-1] = P_pred[1:]
        P_pred[-1] = p_updated

        return P_pred

    def fill_level_battery_power(
        self, Z_charge, Z_discharge, p_t, soc_t, bat_max_pwr, bat_cap
    ):
        """Use valley filling approach to determine battery power at current timestep
        - if abs(p_t) < Z: x_t = 0
        - if abs(p_t) - x_max > Z: x_t = -1 * sign(p_t) * x_max
        - otherwise: x_t = -1 * sign(p_t) * (abs(p_t) - Z)

        Args:
            Z_charge (float): Fill level for charging the battery.
            Z_discharge (float): Fill level for discharging the battery.
            p_t (float): Net load of the house at current timestep.
            soc_t (float): Current state of charge of the battery.
            bat_max_pwr (float): Maximum power of the battery.
            bat_cap (float): Capacity of the battery.

        Returns:
            tuple: The battery power x_t, updated state of charge soc_t,
            and the applied fill level Z_t.
        """
        # Determine fill level Z_t based on net load
        if p_t >= 0:  # net consumption --> battery discharges
            Z_t = Z_discharge
        else:  # net generation --> battery charges
            Z_t = Z_charge

        # Determine battery power using valley filling approach
        x_t = (-1) * np.sign(p_t) * max(0, min(abs(p_t) - abs(Z_t), bat_max_pwr))

        # Enforce feasibility of battery profile wrt. SoC
        # Additional constraints added with safety margins of 10% of capacity
        x_t = min(
            x_t, 0.9 * bat_cap - soc_t
        )  # battery cannot charge more than capacity - soc_t
        x_t = max(
            x_t, -(soc_t - 0.1 * bat_cap)
        )  # battery cannot discharge more than soc_t

        # Update state of charge
        soc_t += x_t

        return x_t, soc_t, Z_t

    def set_fill_levels(self, P_pred):
        """
        Calculate the fill levels Z_charge and Z_discharge for the battery
        based on the predicted net load profile of the house.
        NOTE: Results are so far not that great, similar to greedy. I could
        tune fill levels more towards peak shaving but I don't think that
        users actually care about that or have an incentive to do so.
        They care about maximising self-consumption and cost savings, for
        which greedy is the best strategy.

        Args:
            P_pred (numpy.ndarray): The predicted net load profile of the house.
            We use this profile to estimate suitable fill levels with the goal
            to flatten the total power profile of the house (net load + battery)
            (peak shaving).

        Returns:
            tuple: The fill levels Z_charge and Z_discharge.
        """
        # Z_charge: used when net load is negative (i.e. generation) and battery gets charged
        Z_charge = np.mean(P_pred[P_pred < 0]) if P_pred[P_pred < 0].size != 0 else 0.5
        Z_charge = 0.1 * Z_charge  # reduce Z_charge to 10% of mean value
        # --> better to underestimate Z_charge than overestimate it:
        # if in doubt, better to make battery more "greedy" to increase self-consumption

        # Z_discharge: used when net load is positive (i.e. consumption) and battery gets discharged
        Z_discharge = (
            np.mean(P_pred[P_pred > 0]) if P_pred[P_pred > 0].size != 0 else 0.3
        )
        Z_discharge = 0.1 * Z_discharge  # reduce Z_discharge to 10% of mean value

        return Z_charge, Z_discharge

    ### Not used currently, but might be useful later
    def get_optimal_profile(self, P_load, max_pwr, bat_cap, bat_soc):
        """
        QP optimisation with cvxpy
        Calculates the optimal battery profile that minimizes the 2-norm
        of the total (predicted) power profile of a house.
        Optimal profile used to approximate fill levels Z_charge and Z_discharge.

        Args:
            P_load (list): The net load profile of the house. [kW]
            max_pwr (float): The maximum power of the battery. [kW]
            bat_cap (float): The capacity of the battery. [kWh]
            bat_soc (float): The current/initial state of charge (SoC) of the battery. [kWh]

        Returns:
            numpy.ndarray: The optimal power profile for the battery.
        """
        # GOAL: Find optimal battery profile that minimises 2-norm of total power profile of house
        # Planning horizon: number of timesteps to consider in optimisation
        n = len(P_load)
        # Decision variable x for QP optimisation --> power profile of battery
        x = cp.Variable(n)

        # Parameter: net load profile
        p = cp.Parameter(n)
        p.value = np.array(P_load)

        # Elementwise constraint on x: max battery power
        x_max = max_pwr

        # Lower bound on sum of x_i: -soc_init with safety margin of 10% of capacity
        # Idea: Battery cannot discharge more than soc_init over total planning horizon
        lb = -bat_soc + 0.1 * bat_cap

        # Upper bound on sum of x_i: c_bat-soc_init with safety margin of 10% of capacity
        # Idea: Battery cannot charge more than delta between capacity and soc_init over total planning horizon
        ub = bat_cap - bat_soc - 0.1 * bat_cap

        # Objective: Minimize the 2-norm of the total power profile of the house
        # PEAK SHAVING: We want a total power profile that is as flat as possible
        objective = cp.Minimize(cp.norm(p + x, 2))

        # Constraints
        constraints = [x >= -x_max, x <= x_max, cp.cumsum(x) >= lb, cp.cumsum(x) <= ub]

        # Solve quadratic optimisation problem
        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.ECOS, ignore_dpp=True)

        # Optimal power profile for battery
        x_opt = np.array(x.value)
        return x_opt
