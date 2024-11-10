import logging
from typing import Any

import numpy as np

from components.dev.device import Device
from components.host.sim_host import SimHost

logger: logging.Logger = logging.getLogger("ferntree")


class BaseLoad(Device):
    """Class for uncontrollable baseload."""

    def __init__(
        self, host: SimHost, dev_specs: dict[str, Any], load_profile: list[float]
    ) -> None:
        """Initializes a new instance of the BaseLoad class."""
        super().__init__(host)

        # Annual electricity consumption [kWh] to scale load profile
        self.annual_consumption: float = dev_specs[
            "annual_consumption"
        ]  # Annual electricity consumption [kWh]

        # Set normalised load profile
        self.load_profile: np.ndarray = np.array(load_profile)

        # Current state of the baseload
        self.current_state: dict[str, float] = {"P_base": 0.0}

    def startup(self) -> None:
        """Startup of the baseload
        - Get load profile from database
        - Scale loadprofile to specified annual consumption.
        """
        # load_profile = np.array(self.host.get_load_profile(self.profile_id))
        if abs(self.load_profile.sum() - 1.0) > 1e-6:
            logger.warning(
                f"Load profile not normalized to 1kWh/a: {self.load_profile.sum():.2f} kWh/a"  # noqa: E501
            )

        # Scale load profile to specified annual consumption
        # self.load_profile represents now annual baseload power demand in kW
        self.load_profile = (
            self.load_profile * self.annual_consumption / self.load_profile.sum()
        )
        logger.info(
            f"Baseload: mean {self.load_profile.mean():.2f} kW, max {self.load_profile.max():.2f} kW, min {self.load_profile.min():.2f} kW, {self.load_profile.sum():.2f} kWh"  # noqa: E501
        )

    def timetick(self) -> None:
        """Simulates a single timestep of the baseload."""
        # Update current state of the baseload
        self.current_state["P_base"] = self.load_profile[self.host.current_timestep]
