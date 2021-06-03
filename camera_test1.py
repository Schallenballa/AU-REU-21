import time, sys
import ps_drone                # Imports the PS-Drone-API
import cv2

print("Creating drone object...")
drone = ps_drone.Drone()       # Initializes the PS-Drone-API
print("Beginning Statup...")
drone.startup()                # Connects to the drone and starts subprocesses
print("Performing soft reset...")
drone.reset()
while drone.getBattery()[0] == -1:	time.sleep(0.1)		# Waits until the drone has done its reset
time.sleep(0.5)

drone.useDemoMode(True)

print("Starting the video camera...")
drone.setConfigAllID()                                       # Go to multiconfiguration-mode
drone.sdVideo()                                              # Choose lower resolution (hdVideo() for...well, guess it)
drone.frontCam()                                             # Choose front view
CDC = drone.ConfigDataCount
# while CDC == drone.ConfigDataCount:
#     print(CDC, drone.ConfigDataCount)
#     time.sleep(0.0001) # Wait until it is done (after resync is done)
print("Start")
drone.startVideo()

print("Setting IMC")
IMC = drone.VideoImageCount
stop = False


print("Beginning loop")
while not stop:
    print("Outer loop started...")
    while drone.VideoImageCount==IMC: time.sleep(0.01) #waits until the next video frame
    print("Inner loop started...")
    IMC = drone.VideoImageCount
    key = drone.getKey()
    if key: stop = True
    img = drone.VideoImage
    pImg = cv2.resize(img,(400,100))
    print("Showing img:")
    cv2.imshow('Drones video', pImg)
    cv2.waitKey(1)
# Start video-function
# print("Show")
# drone.showVideo()     
# drone.startVideo()
# 
# time.sleep(2)
# 
# print("Showing video camera...")
# drone.showVideo()

time.sleep(7.5)

print("Hiding video camera...")
drone.hideVideo()

time.sleep(2)

print("Stopping the video camera...")
drone.stopVideo()
print("Program Complete!")
