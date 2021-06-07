import time, sys
import ps_drone                                                               # Import PS-Drone-API


def time_convert(sec):
  mins = sec // 60
  sec = sec % 60
  hours = mins // 60
  mins = mins % 60
  print("Time Lapsed = {0}:{1}:{2}".format(int(hours),int(mins),sec))

drone = ps_drone.Drone()                                                      # Start using drone
drone.startup()


drone.reset()                                                                 # Sets drone's status to good (LEDs turn green when red)
while (drone.getBattery()[0] == -1):  time.sleep(0.1)                         # Wait until the drone has done its reset
print ("Battery: "+str(drone.getBattery()[0])+"%  "+str(drone.getBattery()[1])) # Gives a battery-status
drone.useDemoMode(False)                                                      # Give me everything...fast
drone.getNDpackage(["demo","pressure_raw","altitude","magneto","wifi"])       # Packets, which shall be decoded
time.sleep(1)                                                               # Give it some time to awake fully after reset


NDC = drone.NavDataCount
prevWifi = drone.NavData["wifi"]
while True:
    while drone.NavDataCount == NDC:  time.sleep(0.001)
    start_time = time.time()                   # Wait until next time-unit
    while (drone.NavData["wifi"]==prevWifi):	time.sleep(0.1)	# Sleeps until battery percentage diminishes
    end_time = time.time()
    time_lapsed = end_time - start_time
    time_convert(time_lapsed)
    #if drone.getKey():                end = True                              # Stop if any key is pressed
    NDC=drone.NavDataCount
    print ("Wifi link quality:            "+str(drone.NavData["wifi"]))
    prevWifi=drone.NavData["wifi"]

drone.shutdown()
