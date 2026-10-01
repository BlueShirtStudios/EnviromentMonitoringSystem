from machine import ADC
from machine import Pin

class PhotoSenstiveResistor:
    def __init__(self, c_pin : int):
        self._pin = c_pin
        self._adc_connection = ADC(Pin(self._pin))
        
    def _get_raw_value(self) -> int:
        return self._adc_connection.read_u16()
    
    def get_light_precentage(self) -> float:
        MAX_AMOUNT_RAW = const(65535)
        return (self._get_raw_value()/MAX_AMOUNT_RAW) * 100