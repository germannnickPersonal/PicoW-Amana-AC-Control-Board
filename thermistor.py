from machine import ADC, Pin
import math
import time


class Thermistor:
    def __init__(
        self,
        name,
        adc_pin,
        fixed_resistor,
        r0=30_000.0,
        beta=4_000.0,
        reference_temp_c=25.0,
    ):
        self.name = name
        self.adc = ADC(Pin(adc_pin))
        self.fixed_resistor = float(fixed_resistor)
        self.r0 = float(r0)
        self.beta = float(beta)
        self.reference_temp_k = reference_temp_c + 273.15

    def read_adc(self, samples=16, delay_ms=1):
        total = 0
        for _ in range(samples):
            total += self.adc.read_u16()
            time.sleep_ms(delay_ms)
        return total / samples

    def adc_to_resistance(self, adc_value):
        if adc_value < 100:
            raise RuntimeError(self.name + " thermistor short/open fault")
        if adc_value > 65_435:
            raise RuntimeError(self.name + " thermistor open/short fault")

        return (
            self.fixed_resistor
            * adc_value
            / (65_535.0 - adc_value)
        )

    def resistance_to_celsius(self, resistance):
        inverse_temperature = (
            (1.0 / self.reference_temp_k)
            + math.log(resistance / self.r0) / self.beta
        )
        return (1.0 / inverse_temperature) - 273.15

    def read_temp_C (self):
        adc_value = self.read_adc()
        resistance =  self.adc_to_resistance(adc_value)
        return round(self.resistance_to_celsius(resistance),1)

    def read_temp_F (self):
        return round((self.read_temp_C()*(9/5)) + 32, 1)

    def read_all(self):
        adc_value = self.read_adc()
        resistance = self.adc_to_resistance(adc_value)
        temperature_c = self.resistance_to_celsius(resistance)
        temperature_f = temperature_c * 9.0 / 5.0 + 32.0

        return {
            "name": self.name,
            "adc": adc_value,
            "resistance": resistance,
            "temperature_c": temperature_c,
            "temperature_f": temperature_f,
        }

