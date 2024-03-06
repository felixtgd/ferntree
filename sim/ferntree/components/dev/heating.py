from dev import device, model_2R3C
from ctrl import heating_ctrl

class HeatingSys(device.Device):
    
    def __init__(self, host) -> None:
        
        super().__init__(host)
        
        # Settings
        self.temp_setpoint =    None # temperature setpoint in [K]
        self.deadband =         None # deadband around setpoint
        self.P_heat_max =       None # maximum heating power of system [kW]
        self.heated_area =      None # heated living area [m2]
        self.P_hgain =          None # internal heat gains constant at 3 W/m2


    def startup(self):

        # Thermostat controller for heating system
        self.heating_ctrl = heating_ctrl.HeatingCtrl(self.host, self.temp_setpoint, self.deadband, self.P_heat_max)
        
        # Thermal building model
        self.thermal_model = model_2R3C.ThermalModel(self.host)
        self.thermal_model.T_in = self.temp_setpoint
        self.thermal_model.T_en = self.temp_setpoint

        # Heating device
        # self.heatingDev = HeatingDev()
        
        if self.heated_area is not None:
            self.P_hgain = 3/1e3 * self.heated_area # internal heat gains constant at 3 W/m2
        
        # Initialise current state of the heating system
        self.current_state = {
            "T_in":     self.temp_setpoint,
            "T_en":     self.temp_setpoint,
            "P_hgain":  self.P_hgain,
            "P_heat_th": 0.0
            }

        
    def timetick(self):
        # Get state variables of current timestep from simHost
        T_amb = self.host.env_state["T_amb"]
        P_solar = self.host.env_state["P_solar"]

        # Get state variables of previous timestep from heating system
        T_in = self.current_state["T_in"]
        P_hgain = self.current_state["P_hgain"]
        P_heat_th = self.current_state["P_heat_th"]

        # Calculate required heating power for current timestep
        P_heat_th_next = self.heating_ctrl.set_heating_power(T_in, P_heat_th)

        # Compute thermal response of building
        T_in, T_en = self.thermal_model.compute_thermal_response(T_amb, P_solar, P_hgain, P_heat_th_next)
        
        # Update current state of heating system
        self.current_state["T_in"] = T_in
        self.current_state["T_en"] = T_en
        self.current_state["P_heat_th"] = P_heat_th_next

