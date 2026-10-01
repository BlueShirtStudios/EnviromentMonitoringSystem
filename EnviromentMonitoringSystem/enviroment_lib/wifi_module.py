from machine import Pin
from utime import sleep
import network
import urequests
import rp2

class WifiModule:
    def __init__(self, ssid : str, password : str) -> None:
        self._ssid = ssid               #SSID of connected network
        self._password = password       #Password of the connected network
        self._dashboard_ip = None       #Dashboard IP, in our case Laptop IP
        self._dashboard_broad_port = None   #Broadcating Port of Dashboard
        self._dashboard_url = None      #Generated URL / Link
        self._pico_status = None        #Pico's Wifi Status
        self._wlan = network.WLAN(network.STA_IF)   #WLAN details for easier reading/handling ^-^
        
    def create_dashboard(self, dsh_ip : str, dsh_port : int, dsh_url: str ):
        #Create external dashboard connection
        self._dashboard_ip = dsh_ip
        self._dashboard_broad_port = dsh_port
        self._dashboard_url = dsh_url
        
    def initialize_pico_wifi(self):
        rp2.country("ZA")
        #Activate wifi
        self._wlan.active(True)
        
        #Attempt to get an IP for the pico
        if not self._wlan.isconnected():
            print("Attempting to Connect...")
            self._wlan.connect(self._ssid, self._password)
            timeout = 10
            
            #Tries to establish connection and get IP before timeout hits
            while not self._wlan.isconnected() and timeout > 0:
                print('Waiting to connect...')
                sleep(1)
                timeout -= 1
                
        #Checks if we could establish a connection
        if self._wlan.isconnected():
            #If is connected
            pi_ip = self._wlan.ifconfig()[0]
            print("Successfully Connected!")
            print("IP Address: ", pi_ip)
            self._pico_status = True
            
        else:
            #Else if not could connect
            print("Connection Error.")
            self._pico_status = False
            
    def get_pico_connection_status(self) -> str:
        #Returns a string value to display beyond the terminal
        if self._pico_status == True:
            return f"Wifi Connected."
        
        else: return "No Wifi"
        
    def turn_wifi_off(self):
        #If wifi need to be off, can be toggled externally
        self._wlan.active(False)
        
    def turn_wifi_on(self):
        #If wifi need to be on, can be toggled externally
        self._wlan.active(True)
        
    def send_enviroment_log(self, motion : bool, temperature : float, humidity : float, light_percentage : float):
        if not (self._wlan.isconnected()):
            return None
        
        #Format Payload
        payload = {
                    "detected_motion": motion,
                    "temperature": temperature,
                    "humidity": humidity,
                    "light_percentage": light_percentage
                    }
        
        response = None
        try:
            #Send request to server
            response = urequests.post(self._dashboard_url, json=payload)
            
            #Formatted Result for use
            reponse_data = {
                "http_code" : response.status_code,
                "server_response" : response.json()
            }
            
            return reponse_data
            
        except Exception as e:
            print(f"An error occured: {e}")
            return None
        
        finally:
            if response is not None:
                response.close()