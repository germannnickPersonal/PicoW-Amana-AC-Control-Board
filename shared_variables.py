import _thread
import time
from errorlog import logger

resource_lock = _thread.allocate_lock()

time_init = False

emergency_state = False

modeTempType = 1050
modes = ["off", "fan low", "fan high",
         "cool low", "cool high",
         #"heat low", "heat high",
         #"auto low", "auto high"
         ]

air_temp = 0
indoor_coil = 0
outdoor_coil = 0

current_temps = [air_temp, indoor_coil, outdoor_coil]

def packModeTemp(mode, temp, type):
    m = 100  # Default mode: fan low
    t = 50  # Default temperature offset: midpoint of range
    d = 1000  # Default temperature unit: Fahrenheit
    base = 65  # Fahrenheit setpoint base
    factor = 0.2

    # Select packing values for the requested temperature unit
    if type == "C":
        d = 0
        base = 18.5
        factor = 0.1

    # Encode the requested operating mode
    try:
        m = modes.index(mode)*100
    except ValueError:
        logger.log("Shared Variables", "assign mode packing error")

    # Encode the setpoint as an offset from the unit-specific base
    temp = round(temp, 1)
    t = int((temp - base)/factor)

    send = d + m + t
    if send > 1899 or send < 0:
        logger.log("Shared Variables", "modeTemp packing failed")

    return send

def unpackModeTemp(num):

    if num > 1899 or num < 0:
        logger.log("Shared Variables", "unpack decode error")
        raise ValueError("unpack decode error")

    # Decode the temperature unit
    d = num // 1000
    num = num % 1000
    if d:
        type = "F"
    else:
        type = "C"

    # Decode the operating mode
    m = num // 100
    num = num % 100
    try:
        mode = modes[m]
    except IndexError:
        logger.log("Shared Variales", "mode decode error")
        raise ValueError("invalid mode value")

    # Decode the temperature setpoint
    t = num
    if d:
        temp = 65 + (t * 0.2)
    else:
        temp = 18.5 + (t * 0.1)

    return mode, temp, type