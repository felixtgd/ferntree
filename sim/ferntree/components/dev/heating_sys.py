import logging

from dev import device


logger = logging.getLogger("ferntree")

class HeatingSys(device.Device):
    """Class for a heating system.
    A heating system consists of a thermostat controller, a thermal building model and a heating device.
    Thermostat controller: determines required thermal heating power based on current temperature and setpoint.
    Thermal building model: computes thermal response of building to heating power and ambient temperature.
    Heating device: provides thermal heating power to building and specifies electricity demand.
    """

    def __init__(self, host):
        """Initializes a new instance of the HeatingSys class."""
        super().__init__(host)

        # Components of heating system
        self.thermal_model = None  # thermal building model
        self.heating_ctrl = None  # thermostat controller
        self.heating_dev = None  # heating device, e.g. heat pump or boiler

        # Initialize current state of the heating system
        self.current_state = {
            "T_in": 20.0 + 273.15, # indoor temperature in [K]
            "T_en": 20.0 + 273.15, # building envelope temperature in [K]
            "P_heat_th": 0.0, # thermal heating power in [kW]
            "P_heat_el": 0.0, # electrical heating power in [kW]
        }


    def startup(self):
        """Startup of the heating system.
        - Initializes thermostat controller, thermal building model and heating device
        """
        # TODO: Check that components have been properly initialised
        pass        

    def timetick(self):
        """Simulates a single timestep of the heating system.
        - Gets state variables of current timestep from simHost
        - Gets state variables of previous timestep from heating system
        - Calculates required heating power for current timestep
        - Computes thermal response of building
        - Calculates electricity demand of heating system
        - Updates current state of heating system
        """

        # Get state variables of current timestep from simHost
        T_amb = self.host.env_state["T_amb"]
        P_solar = self.host.env_state["P_solar"]

        # Get state variables of previous timestep from heating system
        T_in = self.current_state["T_in"]
        T_en = self.current_state["T_en"]
        # P_heat_th = self.current_state["P_heat_th"]

        # Heating controller: Determine control signal for heating device based on thermal response of building
        ctrl_signal = self.heating_ctrl.set_ctrl_signal(T_in)

        # Heating device: Calculate heating power (th and el) of heating system based on control signal
        P_heat_th_next, P_heat_el_next = self.heating_dev.set_heating_power(ctrl_signal)

        # Thermal model: Compute thermal response of building
        T_in_next, T_en_next = self.thermal_model.compute_thermal_response(T_in, T_en, T_amb, P_solar, P_heat_th_next)

        # Update current state of heating system
        self.current_state["T_in"] = T_in_next
        self.current_state["T_en"] = T_en_next
        self.current_state["P_heat_th"] = P_heat_th_next
        self.current_state["P_heat_el"] = P_heat_el_next
