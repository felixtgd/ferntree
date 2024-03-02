from component import Component

class HeatingCtrl(Component):

    def __init__(self) -> None:

        super().__init__()
        
        self.temp_setpoint = 20 + 273.15 # temperature setpoint for heating [k]
        self.deadband = 1 # deadband around setpoint
