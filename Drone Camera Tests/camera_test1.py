import time
import ps_drone                # Imports the PS-Drone-API

print("Creating drone object...")
drone = ps_drone.Drone()       # Initializes the PS-Drone-API
print("Beginning Statup...")
drone.startup()                # Connects to the drone and starts subprocesses
print("Performing soft reset...")
drone.reset()
while drone.getBattery()[0] == -1:	time.sleep(0.1)		# Waits until the drone has done its reset
time.sleep(0.5)

print("Starting the video camera...")
drone.startVideo()

time.sleep(2)

print("Showing video camera...")
drone.showVideo()

time.sleep(7.5)

print("Hiding video camera...")
drone.hideVideo()

time.sleep(2)

print("Stopping the video camera...")
drone.stopVideo()
print("Program Complete!")
