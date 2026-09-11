from machine import Pin
import time
import config

class Led:
    def __init__(self, pin = config.LEDPin, blink_time = 0.75):
        self.pin = pin
        self.blink_time = blink_time
        self.LED = Pin("LED", Pin.OUT)

    def blink(self, leave_status, nof_times):
        x = 0
        while x < nof_times:
            time.sleep(self.blink_time)
            if self.LED.value() == 1:
                if leave_status == "ON":
                    self.LED.value(0)
                    time.sleep(self.blink_time)
                    self.LED.value(1)
                if leave_status == "OFF":
                    self.LED.value(1)
                    time.sleep(self.blink_time)
                    self.LED.value(0)
            if self.LED.value() == 0:
                if leave_status == "ON":
                    self.LED.value(0)
                    time.sleep(self.blink_time)
                    self.LED.value(1)
                if leave_status == "OFF":
                    self.LED.value(1)
                    time.sleep(self.blink_time)
                    self.LED.value(0)
            x = x+1

led = Led()