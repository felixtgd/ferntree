from components.host.sim_host import SimHost


class Entity:
    """Base entity class."""

    def __init__(self, host: SimHost) -> None:
        """Initializes a new instance of the Entity class."""
        self.host: SimHost = host
