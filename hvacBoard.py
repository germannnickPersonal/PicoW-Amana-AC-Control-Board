from machine import Pin
import _thread
import time

import config
from errorlog import logger
import shared_variables
from thermistor import Thermistor

class HVACController:
    def __init__(self):
        self.air_temp = Thermistor("Air Temp",
        config.AIR_TEMP, 
        config.AIR_FIXED,
        config.AIR_THERM_R0,
        config.AIR_BETA,
        config.AIR_REF
        )
        self.indoor_coil = Thermistor("Indoor Coil",
        config.INDOOR_COIL, 
        config.INDOOR_COIL_FIXED,
        config.INDOOR_COIL_THERM_R0,
        config.INDOOR_COIL_BETA,
        config.INDOOR_COIL_REF
        )
        self.outdoor_coil = Thermistor("Outdoor Coil",
        config.OUTDOOR_COIL,
        config.OUTDOOR_COIL_FIXED, 
        config.OUTDOOR_COIL_THERM_R0,
        config.OUTDOOR_COIL_BETA,
        config.OUTDOOR_COIL_REF
        )
        self.thermistors = [self.air_temp, self.indoor_coil, self.outdoor_coil]

        self.fan_low = Pin(config.LOW_FAN_RELAY, Pin.OUT, value = 0)
        self.fan_high = Pin(config.HIGH_FAN_RELAY, Pin.OUT, value = 0)
        self.reverse_valve = Pin(config.REVERSING_VALVE_RELAY, Pin.OUT, value = 0)
        self.compressor = Pin(config.COMPRESSOR_RELAY, Pin.OUT, value = 0)
        # Not connecting eletric heating on first runs, testing AC first
        #self.heat1 = Pin(config.ELECTRIC_HEAT_RELAY, Pin.OUT, value = 0)
        #self.heat2 = Pin(config.ELECTRIC_HEAT_RELAY2, Pin.OUT, value = 0)

        self.start_time = time.ticks_ms()
        self.fan_start_ms = 0
        self.fan_stop_ms = 0
        self.compressor_start_ms = 0
        self.compressor_stop_ms = 0
        self.thermal_delay_start_ms = 0

        self.comp_delay_ms = config.COMPRESSOR_DELAY
        self.thermal_delay_ms = config.THERMAL_DELAY
        self.reverse_delay_ms = config.REVERSE_DELAY

        self.indoor_coil_low = config.INDOOR_COIL_LOW
        self.indoor_coil_high = config.INDOOR_COIL_HIGH
        self.outdoor_coil_low = config.OUTDOOR_COIL_LOW
        self.outdoor_coil_high = config.OUTDOOR_COIL_HIGH

        self.thermal_state = False
        self.comp_delay_state = True
        self.reverse_delay_state = False
        self.emergency_state = False

    def therm_check(self):
        for i in range(0,3): 
            temp_temp = self.thermistors[i].read_temp_C()
            with shared_variables.resource_lock:
                shared_variables.current_temps[i] = temp_temp
            print(shared_variables.current_temps)
            if shared_variables.current_temps[i] > 65.5:
                self.emergency_off()
                shared_variables.emergency_state = True
                logger.log("Thermistor Check","Emergency high Temp")

        if config.INDOOR_COIL_HIGH < shared_variables.current_temps[1]:
            self.thermal_state = True
            self.thermal_delay_start_ms = time.ticks_ms()
        if config.INDOOR_COIL_LOW > shared_variables.current_temps[1]:
            self.thermal_state = True
            self.thermal_delay_start_ms = time.ticks_ms()
        if config.OUTDOOR_COIL_HIGH < shared_variables.current_temps[2]:
            self.thermal_state = True
            self.thermal_delay_start_ms = time.ticks_ms()
        if config.OUTDOOR_COIL_LOW > shared_variables.current_temps[2]:
            self.thermal_state = True
            self.thermal_delay_start_ms = time.ticks_ms()

        # Thermal state recovery logic
        if self.thermal_state:
            if self.compressor.value():
                self.comp_state_chg("OFF")

            if (config.INDOOR_COIL_HIGH > shared_variables.current_temps[1]
                and config.INDOOR_COIL_LOW < shared_variables.current_temps[1]
                and config.OUTDOOR_COIL_HIGH > shared_variables.current_temps[2]
                and config.OUTDOOR_COIL_LOW < shared_variables.current_temps[2]):
                if self.thermal_delay_start_ms == 0:
                    logger.log("Thermal State Recovery", 
                               "in thermal state with no start time. Recovering by assigning time")
                    self.thermal_delay_start_ms = time.ticks_ms()
                
                if (time.ticks_diff(time.ticks_ms(), self.thermal_delay_start_ms) 
                    > self.thermal_delay_ms):
                    self.thermal_state = False
                    self.thermal_delay_start_ms = 0

    def temp_op(self):
        with shared_variables.resource_lock:
            packed_state = shared_variables.modeTempType
        mode, temp, type = shared_variables.unpackModeTemp(
            packed_state)
        print(temp)
        if type == "F":
            requested_temp = (temp -32) * (5/9)
        else:
            requested_temp = temp
        print (requested_temp)


        if mode == "off":
            self.comp_state_chg("OFF")
            self.fan_state_chg("OFF")
            #self.heat_state_chg("OFF")
            time.sleep(2)
        elif mode == "fan low":
            self.comp_state_chg("OFF")
            self.fan_state_chg("LOW")
        elif mode == "fan high":
            self.comp_state_chg("OFF")
            self.fan_state_chg("HIGH")
        elif mode == "cool low":
            self.fan_state_chg("LOW")
            if requested_temp + 0.5 < shared_variables.current_temps[0]:
                self.comp_state_chg("ON")
            elif requested_temp - 0.5 > shared_variables.current_temps[0]:  
                self.comp_state_chg("OFF")
        elif mode == "cool high":
            self.fan_state_chg("HIGH")
            if requested_temp + 0.5 < shared_variables.current_temps[0]:                  
                self.comp_state_chg("ON")
            elif requested_temp - 0.5 > shared_variables.current_temps[0]:
                self.comp_state_chg("OFF")
        elif mode == "heat low":
            print("Not there yet homie")
        elif mode == "heat high":
            print("Not there yet homie")
        elif mode == "auto low":
            print("Not there yet homie")
        elif mode == "auto high":
            print("Not there yet homie")
        
    def comp_state_chg(self, req_state):
        if req_state == "OFF":
            if self.compressor.value():
                self.compressor.value(0)
                self.compressor_stop_ms = time.ticks_ms()
                self.comp_delay_state = True
            else:
                return True
        if req_state == "ON":
            if self.compressor.value():
                return True
            if not self.fan_state():
                self.comp_delay_state = True
                return False
            # extra safety check
            if self.comp_delay_state or self.thermal_state:
                if self.compressor.value():
                    self.compressor.value(0)
                    self.compressor_stop_ms = time.ticks_ms()
            if self.comp_delay_state:
                if self.fan_start_ms == 0:
                    self.fan_state_chg("HIGH")
                    return False   
                if (time.ticks_diff(time.ticks_ms(), self.fan_start_ms) 
                        > config.COMPRESSOR_DELAY):
                    self.comp_delay_state = False
            if self.thermal_state:
                return False
            if (not self.comp_delay_state and not self.thermal_state):
                    self.compressor.value(1)
                    self.compressor_start_ms = time.ticks_ms()
                    return True

    # function returns true if either of the fan states are on
    def fan_state(self):
        if self.fan_high.value() or self.fan_low.value():
            return True
        else:
            return False

    def fan_state_chg(self, req):
        was_running = self.fan_state()
        
        if req == "LOW":
            if self.fan_high.value():
                self.fan_high.value(0)
                time.sleep_ms(100) # allow the relay to switch off my switch is 20ms response
                
            if not self.fan_low.value():
                if not was_running:
                    self.fan_start_ms = time.ticks_ms()
                self.fan_low.value(1)
            return True

        elif req == "HIGH":
            if self.fan_low.value():
                self.fan_low.value(0)
                time.sleep_ms(100) # allow the relay to switch off my switch is 20ms response
                
            if not self.fan_high.value():
                if not was_running:
                    self.fan_start_ms = time.ticks_ms()
                self.fan_high.value(1)
            return True
    
        elif req == "OFF":
            if not self.fan_state():
                return True
            if self.comp_delay_state:
                if (time.ticks_diff(time.ticks_ms(), self.compressor_stop_ms) 
                    > config.COMPRESSOR_DELAY):
                    self.fan_high.value(0)
                    self.fan_low.value(0)
                    self.fan_stop_ms = time.ticks_ms()
                    return True
                else:
                    return False
            if self.thermal_state:
                return False
            if self.fan_state() and self.compressor.value():
                self.comp_delay_state = True
                error =  RuntimeError("Fan off request while compressor still on")
                logger.log("HVAC Fan:", error)
                raise error 
            if (not self.compressor.value() 
                and not self.comp_delay_state 
                and not self.thermal_state):
                self.fan_high.value(0)
                self.fan_low.value(0)
                self.fan_stop_ms = time.ticks_ms()
                return True
                

    def emergency_off(self):
        #self.heat1.value(0)
        #self.heat2.value(0)
        self.compressor.value(0)
        self.fan_low.value(0)
        self.fan_high.value(0)
        self.reverse_valve.value(0)