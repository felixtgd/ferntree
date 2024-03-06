from core import entity

class Device(entity.Entity):

    def __init__(self, host) -> None:
        super().__init__(host)

