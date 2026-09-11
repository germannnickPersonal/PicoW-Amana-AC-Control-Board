# Wi-Fi settings
WIFI_SSID = "ZerbraMonkey"  # Placeholder credentials for development
WIFI_PASSWORD = "FalseHorse"

# Watchdog timing limit
WATCH_DOG = 5000  # Configured watchdog timeout (ms); watchdog is currently disabled in main.py

# Onboard LED pin
LEDPin = "LED"  # Pico W typically uses "LED"; some Pico/MicroPython versions use GPIO 25

# 10 A relay pins
# GPIO assignments for attached control devices
LOW_FAN_RELAY = 1  # Low-speed fan relay GPIO
HIGH_FAN_RELAY = 0
REVERSING_VALVE_RELAY = 4

# 20+ A relay outputs
COMPRESSOR_RELAY = 2
ELECTRIC_HEAT_RELAY = 5
ELECTRIC_HEAT_RELAY2 = 6

# Thermistor ADC (analog-to-digital converter) pins
AIR_TEMP = 26
INDOOR_COIL = 27
OUTDOOR_COIL = 28

# Thermistor values
# R0 is the thermistor resistance at the reference temperature
# Measuring these values with a multimeter is recommended
AIR_THERM_R0 = 30000
# Fixed is the known resistor paired with the thermistor for calculations
# Confirm the actual value with a multimeter
AIR_FIXED = 33000
# Beta models the thermistor resistance/temperature curve
AIR_BETA = 4000
# REF is the reference temperature (C) at which R0 is specified
AIR_REF = 25
INDOOR_COIL_THERM_R0 = 30000
INDOOR_COIL_FIXED = 33000
INDOOR_COIL_BETA = 4000
INDOOR_COIL_REF = 25
OUTDOOR_COIL_THERM_R0 = 30000
OUTDOOR_COIL_FIXED = 33000
OUTDOOR_COIL_BETA = 4000
OUTDOOR_COIL_REF = 25

# Compressor and protection delays
COMPRESSOR_DELAY = 15000  # Fan run time (ms) required before compressor startup
REVERSE_DELAY = 300000  # Compressor wait time (ms) after reversing-valve activation
THERMAL_DELAY = 60000  # Recovery delay (ms) before compressor operation can resume

# Thermal limits
# Refrigerant used by the current test system: R22
# All high/low limits are in C for calculation simplicity
INDOOR_COIL_LOW = 10
INDOOR_COIL_HIGH = 54.5
OUTDOOR_COIL_LOW = 10
OUTDOOR_COIL_HIGH = 54.5