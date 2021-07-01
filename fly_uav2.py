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
ALIGN_DATA = (30, 30, 1120, 30)
# Known vlaues for x, y, z-position of each marker and yaw needed for path to
# next marker. The position of each data tuple corresponds with the marker ID.
MARKER_DATA = ((-115, -75, 145, -0.350), ("""x, y, z, yawForNextMarker""")) # TODO: fill in
drone = ps_drone.Drone()

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
    time.sleep(5)
    drone.moveUp()
    time.sleep(6)
    drone.stop()
    time.sleep(1)
# Detects and displays a marker in an image
def detect(camera, detector):
    print("Starting detection...")
    ret, img = camera.read()
    image1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    image = cv2.rotate(image1, cv2.ROTATE_180)
    detection = detector.detect(image)
    if len(detection) != 0:
        cv2.imwrite('/home/pi/Desktop/image.jpg',image)
        #if detection[0]["margin"] >= 10:
       	    #rect = detection[0]["lb-rb-rt-lt"].astype(int).reshape((-1, 1, 2))
            #cv2.polylines(img, [rect], True, BLUE, 2)
       	    #ident = str(detection[0]["id"])
       	    #pos = detection[0]["center"].astype(int) + (-10, 10)
       	    #cv2.putText(img, ident, tuple(pos), cv2.FONT_HERSHEY_SIMPLEX, 1, BLUE, 2)
            #cv2.imshow("IMG", img)
        print(detection, "\n\nEnding detection. Marker detected...",detection[0])
        #cv2.imshow("IMG", img)
        return detection[0]
    print(detection, "\n\nEnding detection...")
    return detection

# Aligns drone with center of marker.
# Successful alignment is determined when the center of the marker is within a 20x20 pixel-box of the detection area's center
# Quadrants:
# II  |  I
#------------
# III |  IV
def align(camera, detector):
    # If the y-value of the AprilTag center is in the III or IV quadrant of the detection zone (leaves a +10-pixel buffer)
    y_pos = detect(camera, detector)["center"][1]
    if y_pos < IMAGE_SIZE[1] // 2 - ALIGN_DATA[1]: # Move forward
        print("Aligning forward...")
        drone.moveForward()
        while detect(camera, detector)["center"][1] < IMAGE_SIZE[1] // 2 - ALIGN_DATA[1]:
            continue
    drone.stop()
    # If the x-value of the AprilTag center is in the I or IV quadrant of the detection zone (leaves a +10-pixel buffer)
    x_pos = detect(camera, detector)["center"][0]
    if x_pos > IMAGE_SIZE[0] // 2 + ALIGN_DATA[0]: # Move right
        print("Aligning right...")
        drone.moveRight()
        while detect(camera, detector)["center"][0] > IMAGE_SIZE[0] // 2 + ALIGN_DATA[0]:
            continue
    # Else if the x-value of the AprilTag center is in the II or III quadrant of the detection zone (leaves a -10-pixel buffer)
    elif x_pos < IMAGE_SIZE[0] // 2 - ALIGN_DATA[0]: # Move left
        print("Aligning left...")
        drone.moveLeft()
        while detect(camera, detector)["center"][0] < IMAGE_SIZE[0] // 2 - ALIGN_DATA[0]:
            continue
    drone.stop()

    #adjust_altitude(ALIGN_DATA[2], ALIGN_DATA[3])

# Orients yaw of drone to yaw needed for path to the next marker
def orient(camera, detector):
    drone_yaw = drone.NavData["demo"][2][2]
    yaw_needed = MARKER_DATA[detect(camera, detector)["id"]][3]
    turn_angle = abs(drone_yaw - yaw_needed)
    if yaw_needed < drone_yaw:
        turn_angle *= -1
    #drone.turnAngle(turn_angle, 1)
    drone.turnAngle(180,1)

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

# Controls program execution
def main():
    camera = cv2.VideoCapture(0)
    detector = apriltag("tagStandard41h12")
    start_drone()

    # Initial alignment
    drone.moveForward()
    while len(detect(camera, detector)) == 0: # Wait for detection
        continue
    drone.stop()
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

main()
