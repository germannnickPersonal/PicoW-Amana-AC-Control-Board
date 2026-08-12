import _thread
from errorlog import logger

resource_lock = _thread.allocate_lock()


# # shared wifi variables
# wifi_connected = False
# restart_wifi = False

emergency_state = False

modeTempType = 1150
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
    m = 100 #defaul fan on low
    t = 50 # defualt temp mid range
    d = 1000 #defualt to F
    base = 65 #defualt temp base for F
    factor = 0.2

    # check Degree type
    if type == "C":
        d = 0
        base = 18.5
        factor = 0.1

    # check mode type
    try:
        m = modes.index(mode)*100
    except ValueError:
        logger.log("Shared Variables", "assign mode packing error")

    # convert temp setting into gradient
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

    # get C or F setting
    d = num // 1000
    num = num % 1000
    if d:
        type = "F"
    else:
        type = "C"

    # get mode
    m = num // 100
    num = num % 100
    try:
        mode = modes[m]
    except IndexError:
        logger.log("Shared Variales", "mode decode error")
        raise ValueError("invalid mode value")

    # get temp
    t = num
    if d:
        temp = 65 + (t * 0.2)
    else:
        temp = 18.5 + (t * 0.1)

    return mode, temp, type