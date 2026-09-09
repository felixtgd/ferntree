from typing import Any

from src.domains.ferntree.components.host.sim_host import SimHost


class Device:
    """Base class for all devices."""

    def __init__(self, host: SimHost) -> None:
        """Initialize a device.

        Args:
            host (SimHost): Simulation host that owns the device.

        """
        super().__init__()
        self.host: SimHost = host
        self.current_state: dict[str, float]

    def startup(self) -> None:
        """Start the device before the simulation begins.

        Returns:
            None: The base implementation performs no work.

        """
        pass

    def timetick(self) -> dict[str, Any] | None:
        """Advance the device by one simulation timestep.

        Returns:
            dict[str, Any] | None: The base implementation returns None.

        """
        pass

    def shutdown(self) -> None:
        """Stop the device after the simulation ends.

        Returns:
            None: The base implementation performs no work.

        """
        pass
