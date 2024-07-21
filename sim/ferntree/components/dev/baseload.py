import logging
import numpy as np

from sim.ferntree.components.dev import device
from sim.ferntree.components.host import sim_host


logger = logging.getLogger("ferntree")


class BaseLoad(device.Device):
    """Class for uncontrollable baseload."""

    def __init__(self, host: sim_host.SimHost, dev_specs: dict, load_profile: list):
        """Initializes a new instance of the BaseLoad class."""
        super().__init__(host)

        # Annual electricity consumption [kWh] to scale load profile
        self.annual_consumption = dev_specs[
            "annual_consumption"
        ]  # Annual electricity consumption [kWh]

        # # Load profile ID to select a synthetic load profile from database
        # if not dev_specs["profile_id"]:
        #     self.profile_id = 0
        # else:
        #     self.profile_id = dev_specs[
        #         "profile_id"
        #     ]  # User specific ID for load profile

        # Set normalised load profile
        self.load_profile = np.array(load_profile)

        self.current_state = {"P_base": 0.0}  # Current state of the baseload

    def startup(self):
        """Startup of the baseload
        - Get load profile from database
        - Scale loadprofile to specified annual consumption
        """
        # load_profile = np.array(self.host.get_load_profile(self.profile_id))
        if abs(self.load_profile.sum() - 1.0) > 1e-6:
            logger.warning(
                f"Load profile not normalized to 1kWh/a: {self.load_profile.sum():.2f} kWh/a"
            )

        # Scale load profile to specified annual consumption
        # self.load_profile represents now annual baseload power demand in kW
        self.load_profile = (
            self.load_profile * self.annual_consumption / self.load_profile.sum()
        )
        logger.info(
            f"Baseload: mean {self.load_profile.mean():.2f} kW, max {self.load_profile.max():.2f} kW, min {self.load_profile.min():.2f} kW, {self.load_profile.sum():.2f} kWh"
        )

    def timetick(self):
        """Simulates a single timestep of the baseload."""

        # Update current state of the baseload
        self.current_state["P_base"] = self.load_profile[self.host.current_timestep]
