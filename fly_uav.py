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

BLUE = 255, 0, 0
LAST_MARKER_ID = 1
IMAGE_SIZE = (640, 360)
# X-axis threshold, altitude, and altitude threshold for navigation
NAV_DATA = (20, 500, 20)
# X- and Y-axis threshold, altitude and altitude threshold for alignment
ALIGN_DATA = (10, 10, 500, 20)
# Known vlaues for x, y, z position of each marker and yaw needed for path to 
# next marker. The position of each data tuple corresponds with the marker ID.
MARKER_DATA = ((x, y, z, yawForNextMarker), (x, y, z, yawForNextMarker)) # TODO: fill in

# Allows manual override shutdown
def exit_gracefully(drone, signal, frame):
    print("Shutting down")
    drone.shutdown()

signal.signal(signal.SIGQUIT, exit_gracefully)

# Starts the drone
def start_drone(drone):   
    print("Starting")
    drone.startup()
    
    print("Resetting")
    drone.reset()
    while drone.getBattery()[0] == -1:    time.sleep(0.1)
    time.sleep(0.5)
    
    print ("Battery: "+str(drone.getBattery()[0])+"%  "+str(drone.getBattery()[1]))
    
    print("Taking off")
    drone.takeoff()

# Detects and displays a marker in an image
def detect(camera, detector):
    ret, img = camera.read()
    image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detection = detector.detect(image)
    if detection["margin"] >= 10:
       rect = detection["lb-rb-rt-lt"].astype(int).reshape((-1, 1, 2))
       cv2.polylines(img, [rect], True, BLUE, 2)
       ident = str(detection["id"])
       pos = detection["center"].astype(int) + (-10, 10)
       cv2.putText(img, ident, tuple(pos), cv2.FONT_HERSHEY_SIMPLEX, 1, BLUE, 2)
    cv2.imshow("IMG", img)
    print(detection)

    return detection

# Aligns drone with center of marker
def align(drone, camera, detector):
    if detect(camera, detector)["center"][1] > IMAGE_SIZE[1] // 2 + ALIGN_DATA[1]: # Move forward
        drone.moveForward()
        while detect(camera, detector)["center"][1] > IMAGE_SIZE[1] // 2 + ALIGN_DATA[1]:
            continue
    elif detect(camera, detector)["center"][1] < IMAGE_SIZE[1] // 2 - ALIGN_DATA[1]: # Move backward
        drone.moveBackward()
        while detect(camera, detector)["center"][1] < IMAGE_SIZE[1] // 2 - ALIGN_DATA[1]:
            continue
    drone.stop()
    if detect(camera, detector)["center"][0] > IMAGE_SIZE[0] // 2 + ALIGN_DATA[0]: # Move right
        drone.moveRight()
        while detect(camera, detector)["center"][0] > IMAGE_SIZE[0] // 2 + ALIGN_DATA[0]:
            continue
    elif detect(camera, detector)["center"][0] < IMAGE_SIZE[0] // 2 - ALIGN_DATA[0]: # Move left
        drone.moveLeft()
        while detect(camera, detector)["center"][0] < IMAGE_SIZE[0] // 2 - ALIGN_DATA[0]:
            continue
    drone.stop()
    
    adjust_altitude(drone, ALIGN_DATA[2], ALIGN_DATA[3])

# Orients yaw of drone to yaw needed for path to the next marker
def orient(drone, camera, detector):
    drone_yaw = drone.NavData["demo"][2][2]
    yaw_needed = MARKER_DATA[detect(camera, detector)["id"]][3]
    turn_angle = abs(drone_yaw - yaw_needed)
    if yaw_needed < drone_yaw:
        turn_angle *= -1
    drone.turnAngle(turn_angle, 1)

# Navigates drone to a detected marker
def marker_navigate(drone, camera, detector):
    drone.moveForward()
    while detect(camera, detector)["center"][1] > IMAGE_SIZE[1] // 2 + ALIGN_DATA[1]:
        if detect(camera, detector)["center"][0] > IMAGE_SIZE[0] // 2 + ALIGN_DATA[0]: # Move right
            drone.moveRight()
            while detect(camera, detector)["center"][0] > IMAGE_SIZE[0] // 2 + ALIGN_DATA[0]:
                continue
            drone.stop()
            drone.moveForward()
        elif detect(camera, detector)["center"][0] < IMAGE_SIZE[0] // 2 - ALIGN_DATA[0]: # Move left
            drone.moveLeft()
            while detect(camera, detector)["center"][0] < IMAGE_SIZE[0] // 2 - ALIGN_DATA[0]:
                continue
            drone.stop()
            drone.moveForward()
        if adjust_altitude(drone, ALIGN_DATA[2], ALIGN_DATA[3]):
            drone.moveForward()
    drone.stop()

# Navigates drone between markers
def navigate(drone, x_pos, camera, detector):
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
        if adjust_altitude(drone, NAV_DATA[1], NAV_DATA[2]):
            drone.moveForward()

# Adjusts drone's altitude
def adjust_altitude(drone, altitude, threshold):
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

# Controls program execution
def main():
    camera = cv2.VideoCapture(0)
    detector = apriltag("tagStandard41h12")
    detect(camera, detector)
    drone = ps_drone.Drone()
    start_drone(drone)
    
    marker_navigate(drone, camera, detector)
    align(drone, camera, detector)
    orient(drone, camera, detector)
    while not detect(camera, detector)["id"] == LAST_MARKER_ID:
        x_pos = drone.NavData["magneto"][0][0]
        navigate(drone, x_pos, camera, detector)
        marker_navigate(drone, camera, detector)
        align(drone, camera, detector)
        orient(drone, camera, detector)

    print("Landing")
    drone.shutdown()
    cv2.destroyAllWindows()
    print("Done")
