"""
This program flies a UAV along a predetermined path.

Author: Nicholas Dunn
Date: 06/24/2021
"""

import time
import signal
import cv2
from apriltag import apriltag
import ps_drone
import os
import board
import busio
import adafruit_lsm303_accel
import adafruit_lsm303dlh_mag
import math

BLUE = 255, 0, 0
LAST_MARKER_ID = 1
IMAGE_SIZE = (640, 360)
# X-axis threshold, altitude, and altitude threshold for navigation
NAV_DATA = (20, 500, 20)
# X- and Y-axis threshold, altitude and altitude threshold for alignment
ALIGN_DATA = (30, 30, 1120, 30)
# Known vlaues for x, y, z-position of each marker and yaw needed for path to
# next marker. The position of each data tuple corresponds with the marker ID.
MARKER_DATA = ((-115, -75, 145, -0.350), ("""x, y, z, yawForNextMarker""")) # TODO: fill in
drone = ps_drone.Drone()
i2c = busio.I2C(board.SCL, board.SDA)
mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)
accel = adafruit_lsm303_accel.LSM303_Accel(i2c)

home_dir = os.path.expanduser('~')
repository_dir = os.path.join(home_dir, 'Desktop/AU-REU-21')

# Allows manual override shutdown
def exit_gracefully(signal, frame):
    print("Shutting down")
    drone.shutdown()

signal.signal(signal.SIGQUIT, exit_gracefully)

# Starts the drone
def start_drone():
    print("Starting")
    drone.startup()

    print("Resetting")
    drone.reset()
    while drone.getBattery()[0] == -1:    time.sleep(0.1)
    time.sleep(0.5)

    print ("Battery: "+str(drone.getBattery()[0])+"%  "+str(drone.getBattery()[1]))

    print("Taking off")
    drone.takeoff()
    time.sleep(10)
    drone.moveUp()
    time.sleep(3)
    drone.stop()
    time.sleep(2)
# Detects and displays a marker in an image
def detect(camera, detector):
    print("Starting detection...")
    ret, img = camera.read()
    image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detection = detector.detect(image)
    cv2.imwrite('~/Desktop/image.png',image)
    if len(detection) != 0:
        #if detection[0]["margin"] >= 10:
       	    #rect = detection[0]["lb-rb-rt-lt"].astype(int).reshape((-1, 1, 2))
            #cv2.polylines(img, [rect], True, BLUE, 2)
       	    #ident = str(detection[0]["id"])
       	    #pos = detection[0]["center"].astype(int) + (-10, 10)
       	    #cv2.putText(img, ident, tuple(pos), cv2.FONT_HERSHEY_SIMPLEX, 1, BLUE, 2)
            #cv2.imshow("IMG", img)
        print(detection, "\n\nEnding detection. Marker detected...",detection[0])
        return detection[0]
    print(detection, "\n\nEnding detection...")
    return detection

# Aligns drone with center of marker.
# Successful alignment is determined when the center of the marker is within a 20x20 pixel-box of the detection area's center
def align(camera, detector):
    # If the y-value of the AprilTag center is in the III or IV quadrant of the detection zone (leaves a +10-pixel buffer)
    y_pos = detect(camera, detector)["center"][1]
    if y_pos > IMAGE_SIZE[1] // 2 + ALIGN_DATA[1]: # Move backward
        drone.moveBackward()
        while detect(camera, detector)["center"][1] > IMAGE_SIZE[1] // 2 + ALIGN_DATA[1]:
            continue
    # Else if the y-value of the AprilTag center is in the I or II quadrant of the detection zone (leaves a -10-pixel buffer)
    elif y_pos < IMAGE_SIZE[1] // 2 - ALIGN_DATA[1]: # Move forward
        drone.moveForward()
        while detect(camera, detector)["center"][1] < IMAGE_SIZE[1] // 2 - ALIGN_DATA[1]:
            continue
    drone.stop()
    # If the x-value of the AprilTag center is in the I or IV quadrant of the detection zone (leaves a +10-pixel buffer)
    x_pos = detect(camera, detector)["center"][0]
    if x_pos > IMAGE_SIZE[0] // 2 + ALIGN_DATA[0]: # Move right
        drone.moveRight()
        while detect(camera, detector)["center"][0] > IMAGE_SIZE[0] // 2 + ALIGN_DATA[0]:
            continue
    # Else if the x-value of the AprilTag center is in the II or III quadrant of the detection zone (leaves a -10-pixel buffer)
    elif x_pos < IMAGE_SIZE[0] // 2 - ALIGN_DATA[0]: # Move left
        drone.moveLeft()
        while detect(camera, detector)["center"][0] < IMAGE_SIZE[0] // 2 - ALIGN_DATA[0]:
            continue
    drone.stop()

    adjust_altitude(ALIGN_DATA[2], ALIGN_DATA[3])

# Orients yaw of drone to yaw needed for path to the next marker
def orient(camera, detector):
    drone_yaw = drone.NavData["demo"][2][2]
    yaw_needed = MARKER_DATA[detect(camera, detector)["id"]][3]
    turn_angle = abs(drone_yaw - yaw_needed)
    if yaw_needed < drone_yaw:
        turn_angle *= -1
    drone.turnAngle(turn_angle, 1)

# Navigates drone to a detected marker
def marker_navigate(camera, detector):
    drone.moveForward()
    # While the AprilTag center's y-value is outside of the acceptable detection range (but still detected, nevertheless)
    while detect(camera, detector)["center"][1] < IMAGE_SIZE[1] // 2 - ALIGN_DATA[1]:
        # If the x-value of the AprilTag's center is to the right of the detection center
        x_pos = detect(camera, detector)["center"][0]
        if x_pos > IMAGE_SIZE[0] // 2 + ALIGN_DATA[0]: # Move right
            drone.moveRight()
            while detect(camera, detector)["center"][0] > IMAGE_SIZE[0] // 2 + ALIGN_DATA[0]:
                continue
            drone.stop()
            drone.moveForward()
        elif x_pos < IMAGE_SIZE[0] // 2 - ALIGN_DATA[0]: # Move left
            drone.moveLeft()
            while detect(camera, detector)["center"][0] < IMAGE_SIZE[0] // 2 - ALIGN_DATA[0]:
                continue
            drone.stop()
            drone.moveForward()
        if adjust_altitude(ALIGN_DATA[2], ALIGN_DATA[3]):
            drone.moveForward()
    drone.stop()

# Navigates drone between markers
def navigate(x_pos, camera, detector):
    drone.moveForward()
    while len(detect(camera, detector)) == 0: # Continue until marker detected
        if drone.NavData["magneto"][0][0] < x_pos - NAV_DATA[0]: # Move right
            drone.moveRight()
            while drone.NavData["magneto"][0][0] < x_pos - NAV_DATA[0]:
                continue
            drone.stop()
            drone.moveForward()
        elif drone.NavData["magneto"][0][0] > x_pos + NAV_DATA[0]: # Move left
            drone.moveLeft()
            while drone.NavData["magneto"][0][0] > x_pos + NAV_DATA[0]:
                continue
            drone.stop()
            drone.moveForward()
        if adjust_altitude(NAV_DATA[1], NAV_DATA[2]):
            drone.moveForward()

# Adjusts drone's altitude
# Passes:  drone, 500, 20
def adjust_altitude(altitude, threshold):
    if drone.NavData["altitude"][3] < altitude - threshold: # Increase altitude
        drone.moveUp()
        while drone.NavData["altitude"][3] < altitude - threshold:
            continue
        drone.stop()
        return True
    elif drone.NavData["altitude"][3] > altitude + threshold: # Decrease altitude
        drone.moveDown()
        while drone.NavData["altitude"][3] > altitude + threshold:
            continue
        drone.stop()
        return True
    return False

# Records x, y, z position and yaw angle data of drone
def record_data():
    with open(os.path.join(repository_dir, 'temp.txt'), 'a') as file:
        print("Magnetometer (micro-teslas): X=%4.1f Y=%4.1f Z=%4.1f"%(mag.magnetic[0],mag.magnetic[1],mag.magnetic[2]))
        file.write(str(int(mag.magnetic[0]))+",")
        file.write(str(int(mag.magnetic[1]))+",")
        file.write(str(int(mag.magnetic[2]))+"\n")
        angle = math.degrees(math.atan2(mag.magnetic[1],mag.magnetic[0]))
        angle-=80
        if angle<0:
            angle+=360
        print("Angle (degrees): "+str(angle))
        file.write(str(angle)+"\n")
        time.sleep(.1)
    file.close()

# Controls program execution
def main():
    with open(os.path.join(repository_dir, 'temp.txt'), 'w') as file:
        file.write("")
    file.close()
    
    camera = cv2.VideoCapture(0)
    detector = apriltag("tagStandard41h12")
    detect(camera, detector)
    start_drone()
    
    # Initial alignment
    print("Initiating alignment")
    align(camera, detector)
    print("Initiating orientation")
    orient(camera, detector)
    
    # Navigate until last marker found and aligned with
#     while not detect(camera, detector)["id"] == LAST_MARKER_ID:
#         x_pos = drone.NavData["magneto"][0][0]
#         print("Initiating navigation")
#         navigate(x_pos, camera, detector)
#         print("Initiating marker-based navigation")
#         marker_navigate(camera, detector)
#         print("Initiating alignment")
#         align(camera, detector)
#         print("Initiating orientation")
#         orient(camera, detector)

    # Shutdown sequence
    print("Landing")
    drone.shutdown()
#     cv2.destroyAllWindows()
    print("Done")
