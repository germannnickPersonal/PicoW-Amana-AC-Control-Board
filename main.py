import micropython
import _thread
import time
from machine import WDT

import thermistor
import shared_variables
from hvacBoard import HVACController
import web_server
import config

# Set aside emergency RAM
micropython.alloc_emergency_exception_buf(100)

# initiate controller
controller = HVACController()

# initiate thread for web server
wlan_out = 0
_thread.start_new_thread(web_server.run_web_server, ())

# start watch dog
#wdt = WDT(timeout = 8000)
# watch dog can cause issues while debugging.
# Communication between the device and the IDE
# can be interrupted without activating the 
# watch dog. Best practice seems to be debug without
# watch dog and implement watch dog when running.

#start while true loop
while True:
    if not shared_variables.emergency_state:
        controller.therm_check()
        controller.temp_op()
    # # Check make sure web server is running
    # if shared_variables.wifi_connected:
    #     wlan_out = 0
    # else:
    #     wlan_out += 1
    #     if wlan_out >= 180:
    #         shared_variables.restart_wifi = True
    #         wlan_out = 0


    time.sleep(1)
    #wdt.feed()
