import numpy as np 
from component import Component

class ThermalModel(Component):

    def __init__(self) -> None:

        super().__init__()

        # SFH F Var3 Model parameters
        self.Ai = 1.72
        self.Ce = 16.39
        self.Ci = 2.02
        self.Rea = 13.26
        self.Ria = 24.38
        self.Rie = 0.53

        self.heated_area = 158 # heated living area [m2]
        #self.Pg = np.ones(len(Ta)) * 3/1e3 * heated_area # internal heat gains constant at 3 W/m2