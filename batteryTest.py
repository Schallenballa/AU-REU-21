#This program is designed to test the stability of the battery of the Raspberry Pi & the AR.Drone 2.0's output USB connection

import time, sys
import ps_drone													# Import PS-Drone-API
import cv2


def time_convert(sec):
  mins = sec // 60
  sec = sec % 60
  hours = mins // 60
  mins = mins % 60
  print("Time Lapsed = {0}:{1}:{2}".format(int(hours),int(mins),sec))

drone = ps_drone.Drone()										# Start using drone
drone.startup()													# Connects to drone and starts subprocesses


drone.reset()													# Sets drone's status to good (LEDs turn green when red)
while (drone.getBattery()[0]==-1):	time.sleep(0.1)				# Waits until drone has done its reset

print ("Battery: "+str(drone.getBattery()[0])+"%  "+str(drone.getBattery()[1]))	# Gives a battery-status

prevBatt = drone.getBattery()[0]
while (drone.getBattery()[0] > 20):
    start_time = time.time()
    while (drone.getBattery()[0]==prevBatt):	time.sleep(0.1)	# Sleeps until battery percentage diminishes
    end_time = time.time()
    time_lapsed = end_time - start_time
    time_convert(time_lapsed)
    print("Battery: "+str(drone.getBattery()[0])+"% ")          # Prints the newest battery reading
    prevBatt=drone.getBattery()[0]
