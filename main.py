import micropython
import _thread
import time
from machine import WDT


import thermistor
import shared_variables
from hvacBoard import HVACController
import web_server
import config
from led import led

# Reserve RAM for emergency exception reporting
micropython.alloc_emergency_exception_buf(100)

# Initialize the HVAC controller
controller = HVACController()

# Start the web server on the second thread
wlan_out = 0
_thread.start_new_thread(web_server.run_web_server, ())

# Blink the onboard LED to confirm startup
led.blink("OFF", 3)

# Watchdog placeholder (currently disabled)
#wdt = WDT(timeout = 8000)

# Main HVAC control loop
while True:
    if not shared_variables.emergency_state:
        controller.therm_check()
        controller.temp_op()

    time.sleep(1)
    #wdt.feed()