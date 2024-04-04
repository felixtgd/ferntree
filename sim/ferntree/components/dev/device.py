from core import entity


class Device(entity.Entity):
    def __init__(self, host):
        super().__init__(host)

    def startup(self):
        pass

    def shutdown(self):
        pass
