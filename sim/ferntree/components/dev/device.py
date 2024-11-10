from typing import Any

from components.core.entity import Entity
from components.host.sim_host import SimHost


class Device(Entity):
    """Base class for all devices."""

    def __init__(self, host: SimHost) -> None:
        """Initializes a new instance of the Device class."""
        super().__init__(host)

        self.current_state: dict[str, float]

    def startup(self) -> None:
        """Startup of the device."""
        pass

    def timetick(self) -> Any:
        """Simulates a single timestep of the device."""
        pass

    def shutdown(self) -> None:
        """Shutdown of the device."""
        pass
