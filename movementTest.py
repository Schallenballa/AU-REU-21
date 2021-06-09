import time
import ps_drone
import sys
import signal

def exit_gracefully(signal, frame):
    print("Shutting down")
    drone.shutdown()

signal.signal(signal.SIGQUIT, exit_gracefully)

print("Initializing")
drone = ps_drone.Drone()       # Initializes the PS-Drone-API

print("Starting")
drone.startup()                # Connects to the drone and starts subprocesses

print("Resetting")
drone.reset()
while drone.getBattery()[0] == -1:	time.sleep(0.1)		# Waits until the drone has done its reset
time.sleep(0.5)

print ("Battery: "+str(drone.getBattery()[0])+"%  "+str(drone.getBattery()[1]))	# Gives a battery-status

print("Taking off")
drone.takeoff()                # Drone starts
print("Sleeping")
time.sleep(10)                # Gives the drone time to start

print("Turning")
drone.turnAngle(-90.0, 1)
time.sleep(0)

# print("Moving Left")
# drone.moveLeft()
# time.sleep(1)
# drone.stop()
# time.sleep(20)

print("Landing")
drone.shutdown()                   # Drone lands
print("Done")
