# This is a program designed to take advantage of ps_drone.py's self.at("REF" [DECIMAL --> BINARY]) function to set the altitude to a given parameter

import time
import ps_drone                # Imports the PS-Drone-API
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

#print("Taking off")
#drone.takeoff()                # Drone starts
#print("Sleeping")
print("Sleeping for 3 seconds...")
time.sleep(3)
print("Calling setAltitude function!")  
drone.setAltitude()
