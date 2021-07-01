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
# Known vlaues for x, y, z-position and angle of each marker and yaw needed for path
# to next marker. The position of each data tuple corresponds with the marker ID.
MARKER_DATA = ((70, -20, 105, 265, 225), ("""x, y, z, yawForNextMarker""")) # TODO: fill in
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
        # Takes the picture with the currently-detected AprilTag and saves it to the Desktop
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

# Orients yaw of drone to yaw needed for path to the next marker
def orient(tag_id, index):
    drone_yaw = math.degrees(math.atan2(mag.magnetic[1],mag.magnetic[0])) - 80
    if drone_yaw<0:
        drone_yaw+=360
    yaw_needed = MARKER_DATA[tag_id][index]
    turn_angle = abs(drone_yaw - yaw_needed)
    if yaw_needed < drone_yaw:
        turn_angle *= -1
    drone.turnAngle(turn_angle, 1)

# Aligns drone with center of marker.
# Successful alignment is determined when the center of the marker is within a 20x20 pixel-box of the detection area's center
def align(tag_id):
    for i in range(2):
        # If the y-value of the AprilTag center is in the I or II quadrant of the detection zone (leaves a -10-pixel buffer)
        if mag.magnetic[1] < MARKER_DATA[tag_id][1] - ALIGN_DATA[1]: # Move forward
            drone.moveForward()
            while mag.magnetic[1] < MARKER_DATA[tag_id][1] - ALIGN_DATA[1]:
                continue
        drone.stop()
        # If the y-value of the AprilTag center is in the III or IV quadrant of the detection zone (leaves a +10-pixel buffer)
        if mag.magnetic[1] > MARKER_DATA[tag_id][1] + ALIGN_DATA[1]: # Move backward
            drone.moveBackward()
            while mag.magnetic[1] > MARKER_DATA[tag_id][1] + ALIGN_DATA[1]:
                continue
        # If the x-value of the AprilTag center is in the I or IV quadrant of the detection zone (leaves a +10-pixel buffer)
        if mag.magnetic[0] < MARKER_DATA[tag_id][0] - ALIGN_DATA[0]: # Move right
            drone.moveRight()
            while mag.magnetic[0] < MARKER_DATA[tag_id][0] - ALIGN_DATA[0]:
                continue
        # If the x-value of the AprilTag center is in the II or III quadrant of the detection zone (leaves a -10-pixel buffer)
        if mag.magnetic[0] > MARKER_DATA[tag_id][0] + ALIGN_DATA[0]: # Move left
            drone.moveLeft()
            while mag.magnetic[0] > MARKER_DATA[tag_id][0] + ALIGN_DATA[0]:
                continue
        drone.stop()

        adjust_altitude(ALIGN_DATA[2], ALIGN_DATA[3])

# Navigates drone between markers
def navigate(x_pos, camera, detector):
    detection = detect(camera, detector)
    drone.moveForward()
    start_time = time.time()
    end_time = start_time+0.1
    # While there is currently no marker detected
    while len(detection) == 0: # Continue until marker detected
        start_time=time.time()
        # Will run every 1/10th of a second (0.1)
        if start_time>=end_time:
            record_data() # Records a data point to both files
            end_time = start_time+0.1
        if mag.magnetic[0] < x_pos - NAV_DATA[0]: # Move right
            drone.moveRight()
            while mag.magnetic[0] < x_pos - NAV_DATA[0]:
                continue
            drone.stop()
            drone.moveForward()
        elif mag.magnetic[0] > x_pos + NAV_DATA[0]: # Move left
            drone.moveLeft()
            while mag.magnetic[0] > x_pos + NAV_DATA[0]:
                continue
            drone.stop()
            drone.moveForward()
        if adjust_altitude(NAV_DATA[1], NAV_DATA[2]):
            drone.moveForward()
        detection = detect(camera, detector)
    drone.stop()
    return detection["id"]

# Adjusts drone's altitude
def adjust_altitude(altitude, threshold):
    if mag.magnetic[2] < altitude - threshold: # Increase altitude
        drone.moveUp()
        while mag.magnetic[2] < altitude - threshold:
            continue
        drone.stop()
        return True
    elif mag.magnetic[2] > altitude + threshold: # Decrease altitude
        drone.moveDown()
        while mag.magnetic[2] > altitude + threshold:
            continue
        drone.stop()
        return True
    return False

# Clears & overrites the previous data files
def initialize_files():
    with open(os.path.join(repository_dir, 'magData.txt'), 'w') as file:
        file.write("")
    file.close()
    with open(os.path.join(repository_dir, 'yawData.txt'), 'w') as file:
        file.write("")
    file.close()

# Records x, y, z position and yaw angle data of drone
def record_data():
    print("Recording data points...")
    with open(os.path.join(repository_dir, 'magData.txt'), 'a') as file:
        print("Magnetometer (micro-teslas): X=%4.1f Y=%4.1f Z=%4.1f"%(mag.magnetic[0],mag.magnetic[1],mag.magnetic[2]))
        file.write(str(int(mag.magnetic[0]))+",")
        file.write(str(int(mag.magnetic[1]))+",")
        file.write(str(int(mag.magnetic[2]))+"\n")
    file.close()
    with open(os.path.join(repository_dir, 'yawData.txt'), 'a') as file:
        angle = math.degrees(math.atan2(mag.magnetic[1],mag.magnetic[0])) - 80
        if angle<0:
            angle+=360
        print("Angle (degrees): "+str(angle))
        file.write(str(angle)+"\n")
    file.close()

# Controls program execution
def main():
    camera = cv2.VideoCapture(0)
    detector = apriltag("tagStandard41h12")
    initialize_files()
    start_drone()

    # Initial alignment
    detection = detect(camera, detector)
    while len(detection) == 0: # Wait for detection
        detection = detect(camera, detector)
    print("Orienting")
    orient(detection["id"], 3)
    print("Aligning")
    align(detection["id"])

    # Navigate until last marker found and aligned with
#     while not detection["id"] == LAST_MARKER_ID:
#         print("Orienting for next marker")
#         orient(detection["id"], 4)
#         print("Navigating")
#         x_pos = drone.NavData["magneto"][0][0]
#         detection = navigate(x_pos, camera, detector)
#         print("Orienting")
#         orient(detection["id"], 3)
#         print("Aligning")
#         align(camera, detector)

    # Shutdown sequence
    print("Landing")
    drone.shutdown()
#     cv2.destroyAllWindows()
    print("Done")

main()
