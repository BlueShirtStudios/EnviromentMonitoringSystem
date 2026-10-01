from enviroment_lib.photo_sens_res import PhotoSenstiveResistor
from enviroment_lib.analytics_container import AnalyticsContainer
from enviroment_lib.pico_i2c_lcd import I2cLcd

from machine import Pin, I2C
from dht import DHT11
from utime import sleep

"""
This is a class that serves as the main driver for the enviroment monitoring system. It allows for easier use to build this project and allows
for easier expansions in a controlled enviroment.
"""

class MonitorSystem:
    def __init__(self, onboard_led : int):
        #LEDs
        self._onboard_led = Pin(onboard_led, Pin.OUT)
        self._red_led: Pin | None = None
        self._green_led: Pin | None = None
        
        #Hard Components
        self._motion_sensor: Pin | None = None
        self._lcd_display: I2cLcd | None = None
        self._weather_station: DHT11 | None = None
        self._photo_sens_resistor: PhotoSenstiveResistor | None = None
        
        self._session_analytics :dict[int, AnalyticsContainer] = {}
        
    def create_onboard_led(self, gpio_pin : int):
        self._onboard_led = Pin(gpio_pin, Pin.OUT)
        
    def create_red_led(self, gpio_pin : int):
        self._red_led = Pin(gpio_pin, Pin.OUT)
        
    def create_green_led(self, gpio_pin : int):
        self._green_led = Pin(gpio_pin, Pin.OUT)
            
    def create_motion_sensor(self, gpio_pin : int):
        self._motion_sensor = Pin(gpio_pin, Pin.IN, Pin.PULL_DOWN)
        
    def create_weather_station(self, gpio_pin : int):
        self._weather_station = DHT11(Pin(gpio_pin))
        
    def create_light_detector(self, gpio_pin : int):
        self._photo_sens_resistor = PhotoSenstiveResistor(gpio_pin)
        
    def create_lcd_display(self, sda_pin : int, scl_pin, i2c_addr: int, num_rows:int, num_cols : int, ass_freq = 400000):
        #Create i2c object
        i2c = I2C(0, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=ass_freq)
        
        #Create our lcd display
        self._lcd_display = I2cLcd(i2c, i2c_addr, num_rows, num_cols)
        
    def _toggle_light(self, light : Pin):
        light.toggle()
    
    def _start_all_lights(self):
        self._onboard_led.on()
        if self._red_led:
            self._red_led.on()
            
        if self._green_led:
            self._green_led.on()
        
    def _end_all_lights(self):
        self._onboard_led.off()
        if self._red_led:
            self._red_led.off()
            
        if self._green_led:
            self._green_led.off()
        
        if self._lcd_display:
            self._lcd_display.clear()
            self._lcd_display.move_to(0, 0)
        
    def init_all_components(self):
        #Show startup feedback
        self._start_all_lights()
        
        if self._lcd_display:
            self._lcd_display.display_on()
            self._lcd_display.move_to(0, 0)
            self._lcd_display.putstr("Starting System...")
        
        #Allow hardware to boot
        sleep(5)
        
        #Show that all components are booted
        self._end_all_lights()
        
    def _handle_reading(self, motion : bool):
        #Turn the LEDs on and off based on which branch was triggered
        #If there was motion
        if motion == True:
            if self._red_led:
                self._red_led.on()
                
            if self._green_led:
                self._green_led.off()
            
        #If there was no motion
        else:
            if self._red_led:
                self._red_led.off()
                
            if self._green_led:
                self._green_led.on()
        
    def scan_enviroment_for_motion(self) -> bool:
        if self._motion_sensor:
            #Initialize
            was_motion_detected: bool = False
            
            #Get the reading from the sensor
            sensor_reading: int = self._motion_sensor.value()
            if (sensor_reading == 1):
                was_motion_detected = True
                
            else:
                was_motion_detected = False
                
            #Let the circuit react to the outcome of the motion
            self._handle_reading(was_motion_detected)
            
            #Return the outcome
            return was_motion_detected
        
        else:
            return False
    
    def scan_enviroment_temperature(self) -> float:
        if self._weather_station:
            self._weather_station.measure()
            return self._weather_station.temperature()
        
        else:
            return 0
    
    def scan_enviroment_humidity(self) -> float:
        if self._weather_station:
            self._weather_station.measure()
            return self._weather_station.humidity()
        
        else:
            return 0
        
    def scan_enviroment_light_percentage(self) -> float:
        if self._photo_sens_resistor:
            return round(self._photo_sens_resistor.get_light_precentage(), 2)
        
        else:
            return 0
    
    def save_session_analytics(self, motion : bool, temperature : float, humidity : float, light_percentage : float):
        #Create a new container object
        container = AnalyticsContainer()
        container._motion = motion
        container._temperature = temperature
        container._humidity = humidity
        container._light_percentage = light_percentage
        
        #Add to our session stats
        #Create dictionary key
        key = len((self._session_analytics.keys())) + 1
        
        #Add our entry to the dictionary
        self._session_analytics[key] = container
        
    def total_log_entries(self):
        return len(self._session_analytics.keys())
    
    def clean_session_analytics(self):
        self._session_analytics.clear()
        
    def display_motion_on_screen(self, motion : bool):
        if self._lcd_display:
            #Build motion message
            motion_msg = self._get_motion_to_str(motion)
            
            #Display the message on the screen
            self._lcd_display.clear()
            self._lcd_display.move_to(0, 0)
            self._lcd_display.putstr(str(motion_msg))
            
            #Allow display time
            sleep(1)
            
    def display_enviroment_info_on_screen(self, temp : float, hum : float, light : float):
        if self._lcd_display:
            #Display the temperature and humuidity 
            self._lcd_display.clear()
            self._lcd_display.move_to(0, 0)
            self._lcd_display.putstr(str(f"T: {temp}, H: {hum}%"))
            
            #Display the light percentage
            self._lcd_display.move_to(0, 1)
            self._lcd_display.putstr(str(f"L: {light}%"))
            
            #Allow display time
            sleep(1)
    
    def _get_motion_to_str(self, motion : bool):
        if (motion == True):
            return "Motion Detected"
        
        else : return "No Motion Detected"
        
    def shutdown_system(self):
        if self._onboard_led:
            self._onboard_led.off()
            
        if self._red_led:
            self._red_led.off()
            
        if self._green_led:
            self._green_led.off()
        
        if self._lcd_display:
            self._lcd_display.display_off()
            
    def display_content_on_first_line(self, content : str):
        if self._lcd_display:
            self._lcd_display.clear()
            self._lcd_display.move_to(0, 0)
            self._lcd_display.putstr(content)