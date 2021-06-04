#########
# getNavData.py
# This program is part of the online PS-Drone-API-tutorial on www.playsheep.de/drone.
# It shows how to read out selected NavData-values from a Parrot AR.Drone 2.0 using the PS-Drone-API. The drone will stay on the ground.
# Dependencies: a POSIX OS, PS-Drone-API 2.0 beta or higher.
# (w) J. Philipp de Graaff, www.playsheep.de, 2014
##########
# LICENCE:
#   Artistic License 2.0 as seen on http://opensource.org/licenses/artistic-license-2.0 (retrieved December 2014)
#   Visit www.playsheep.de/drone or see the PS-Drone-API-documentation for an abstract from the Artistic License 2.0.
###########

##### Suggested clean drone startup sequence #####
import time, sys
import ps_drone                                                               # Import PS-Drone-API

drone = ps_drone.Drone()                                                      # Start using drone					
drone.startup()                                                               # Connects to drone and starts subprocesses

drone.reset()                                                                 # Sets drone's status to good (LEDs turn green when red)
while (drone.getBattery()[0] == -1):  time.sleep(0.1)                         # Wait until the drone has done its reset
print ("Battery: "+str(drone.getBattery()[0])+"%  "+str(drone.getBattery()[1])) # Gives a battery-status
drone.useDemoMode(False)                                                      # Give me everything...fast
drone.getNDpackage(["demo","pressure_raw","altitude","magneto","wifi"])       # Packets, which shall be decoded
time.sleep(1)                                                               # Give it some time to awake fully after reset

##### Mainprogram begin #####
NDC = drone.NavDataCount
start = time.monotonic() #end = False
while time.monotonic() < start + : #not end:    
    while drone.NavDataCount == NDC:  time.sleep(0.001)                       # Wait until next time-unit
    #if drone.getKey():                end = True                              # Stop if any key is pressed
    NDC=drone.NavDataCount
    print ("-----------")
    print ("Aptitude [X,Y,Z] :            "+str(drone.NavData["demo"][2]))
    print ("Altitude / sensor / pressure: "+str(drone.NavData["altitude"][3])+" / "+str(drone.State[21])+" / "+str(drone.NavData["pressure_raw"][0]))
    print ("Megnetometer [X,Y,Z]:         "+str(drone.NavData["magneto"][0]))
    print ("Wifi link quality:            "+str(drone.NavData["wifi"]))
    
drone.shutdown()