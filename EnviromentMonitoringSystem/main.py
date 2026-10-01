from enviroment_lib.monitor_sys import MonitorSystem
from enviroment_lib.wifi_module import WifiModule
from utime import sleep
import _thread
import gc

#Global Declarations for threading
stats_lock = _thread.allocate_lock()
latest_stats = None
is_running = True

def main():
    #Create Monitor Object
    enviroment_monitor = MonitorSystem(25)
    
    #Create objects for all our components
    enviroment_monitor.create_red_led(13)
    enviroment_monitor.create_green_led(17)
    enviroment_monitor.create_motion_sensor(20)
    enviroment_monitor.create_weather_station(22)
    enviroment_monitor.create_light_detector(27)
    enviroment_monitor.create_lcd_display(0, 1, 0x27, 4, 20)
    
    #Wifi Chip
    wifi = WifiModule("Your Wifi", "Wifi Password")
    wifi.create_dashboard("192.168.0.240", 5000, "http://192.168.0.240:5000/api/data")
    
    #Show initial state of system on startup and initialize components
    #External Components
    enviroment_monitor.init_all_components()
    
    #Embedded wifi chip
    enviroment_monitor.display_content_on_first_line("Establish Wifi.")
    wifi.initialize_pico_wifi()
    enviroment_monitor.display_content_on_first_line(wifi.get_pico_connection_status())
    
    #Start a thread for readings - Thread 1
    _thread.start_new_thread(sensor_worker, (enviroment_monitor,))
    
    #Main thread for wifi - Thread 0
    while (True):
        try:
            current_stats = None
            outcome = "None"
            with stats_lock:
                if latest_stats is not None:
                    current_stats = latest_stats
            
            if current_stats:
                outcome = send_analytics(wifi, current_stats)
                gc.collect()
                
            #Allow cooldown
            sleep(3)
            
        except KeyboardInterrupt:
            break
        
        finally:
            is_running = False
            sleep(0.6)
            enviroment_monitor.shutdown_system()
            print("Done") 
    
    
def read_enviroment(enviroment_monitor : MonitorSystem) -> tuple:
    #Read from the enviroment
    motion = enviroment_monitor.scan_enviroment_for_motion()
    temperature = enviroment_monitor.scan_enviroment_temperature()
    humidity = enviroment_monitor.scan_enviroment_humidity()
    light_percentage = enviroment_monitor.scan_enviroment_light_percentage()
                
    #Test
    print(motion)
    print(temperature)
    print(humidity)
    print(light_percentage)
                
    #Display Stats on the screen
    enviroment_monitor.display_motion_on_screen(motion)
    enviroment_monitor.display_enviroment_info_on_screen(temperature, humidity, light_percentage)
    
    #Save the stats for a session
    enviroment_monitor.save_session_analytics(motion, temperature, humidity, light_percentage)
    print("Save stats")
                            
    #Manual check to free memory
    if (enviroment_monitor.total_log_entries() == 5):
            enviroment_monitor.clean_session_analytics()
       
    #Return the result back to main             
    return motion, temperature, humidity, light_percentage

def send_analytics(wifi : WifiModule, stats : tuple[bool, float, float, float]) -> str:
    #Sends the stats to the dashboard
    print(f"Sending: {stats}")
    response = wifi.send_enviroment_log(stats[0], stats[1], stats[2], stats[3])
    
    if response:
        print("Sent")
        
    else: print("nope")
    
    #Checks if there was a respose 
    if response and isinstance(response.get("server_response"), dict):
        #If there was 
        return response["server_response"].get("status", "No status key")
    
    #If there was not
    return "Nothing"

def sensor_worker(enviroment_monitor: MonitorSystem):
    global latest_stats
    
    while is_running:
        try:
            stats = read_enviroment(enviroment_monitor)   
            #Safely store latest readings for Core 0
            with stats_lock:
                #Read and process environment data
                latest_stats = stats
                
            sleep(0.5)
            
        except Exception as e:
            print(f"Sensor thread error: {e}")
            sleep(1)

if __name__ == "__main__":
    main()