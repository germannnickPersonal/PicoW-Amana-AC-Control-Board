# WIFI settings
WIFI_SSID = "placeholder"
WIFI_PASSWORD = "stuffy383"

# Watch Dog timing limit
WATCH_DOG = 5000 #Time in ms that that watch dog will reset the pico if not responding

# 10 amp Relay pins
# Pins are the GPIO pins the devices will be attached at
LOW_FAN_RELAY = 1# instert Pin#
HIGH_FAN_RELAY = 2
REVERSING_VALVE_RELAY = 4

# 20+ amp relays
COMPRESSOR_RELAY = 3
ELECTRIC_HEAT_RELAY = 5
ELECTRIC_HEAT_RELAY2 = 6

# Thermistor ADC (Anolog to Digital Converter) pins
AIR_TEMP = 26
INDOOR_COIL = 27
OUTDOOR_COIL = 28

# Thermister Values
# R0 is the thermistor resistor value at reference temp
# Recommend measuring these with a multimeter
AIR_THERM_R0 = 30000
# Fixed is the fixed resistor used with that thermistor for calcs
# confirm with a multimeter
AIR_FIXED = 33000
# Ref is the Beta value for the change in resistance per degree change
AIR_BETA = 4000
# Ref is the reference temperature (in C) that the thermistor resistance is measured at
AIR_REF = 25
INDOOR_COIL_THERM_R0 = 30000
INDOOR_COIL_FIXED = 33000
INDOOR_COIL_BETA = 4000
INDOOR_COIL_REF = 25
OUTDOOR_COIL_THERM_R0 = 30000
OUTDOOR_COIL_FIXED = 33000
OUTDOOR_COIL_BETA = 4000
OUTDOOR_COIL_REF = 25

# Time Delays for compressor
COMPRESSOR_DELAY = 15000 # the time(ms_sec) the fans are on before the compressor can turn on
REVERSE_DELAY = 300000  # time (ms_sec) the compressor must wait before turning on after reversal valve activation
THERMAL_DELAY = 15000 # time (ms_sec) compressor will wait until

# Thermal limits
# Refridgerant used: R22 (note this here)
# All high and low are in C for equation simplicity
INDOOR_COIL_LOW = 12
INDOOR_COIL_HIGH = 57
OUTDOOR_COIL_LOW = 12
OUTDOOR_COIL_HIGH = 57