import time
import signal
import cv2
from apriltag import apriltag
import ps_drone
import os
#import board
#import busio
#import adafruit_lsm303_accel
#import adafruit_lsm303dlh_mag
import math

BLUE = 255, 0, 0
LAST_MARKER_ID = 1
IMAGE_SIZE = (640, 360)
# X-axis threshold, altitude, and altitude threshold for navigation
NAV_DATA = (20, 500, 20)
# X- and Y-axis threshold, altitude and altitude threshold for alignment
ALIGN_DATA = (30, 30, -35, 30)
# Known vlaues for x, y, z-position and angle of each marker and yaw needed for path
# to next marker. The position of each data tuple corresponds with the marker ID.
MARKER_DATA = ((-70, 55, -105, 275, 70), (-70, 55, -105, 350, 355)) # TODO: fill in
drone = ps_drone.Drone()
#i2c = busio.I2C(board.SCL, board.SDA)
#mag = adafruit_lsm303dlh_mag.LSM303DLH_Mag(i2c)
#accel = adafruit_lsm303_accel.LSM303_Accel(i2c)

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
    drone.useDemoMode(False)                                                      # Give me everything...fast
    drone.getNDpackage(["demo","pressure_raw","altitude","magneto","wifi"])       # Packets, which shall be decoded
    print("Taking off")
    drone.takeoff()
    time.sleep(10)
    drone.moveUp()
    time.sleep(5)
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
    #drone_yaw = drone.NavData["demo"][2][2]
    #if drone_yaw<0:
    #    drone_yaw+=360
    #print("Current yaw: ",drone_yaw)
    yaw_needed = MARKER_DATA[tag_id][index]
    print("Yaw needed: ",yaw_needed)
    #turn_angle = abs(drone_yaw - yaw_needed)
    #print("Calculated turn angle: ",turn_angle)
#     if turn_angle > 180:
#         turn_angle = 360 - turn_angle
    #if yaw_needed < drone_yaw:
    #    turn_angle *= -1
    #print("Final turn angle: ",turn_angle)
    #drone.turnAngle(turn_angle, 1)
    drone.turnAngle(yaw_needed,1)
    print("Finished turning...")
# Aligns drone with center of marker.
# Successful alignment is determined when the center of the marker is within a 20x20 pixel-box of the detection area's center
# def align(tag_id):
#     for i in range(2):
#         # If the y-value of the AprilTag center is in the I or II quadrant of the detection zone (leaves a -10-pixel buffer)
#         if mag.magnetic[1] < MARKER_DATA[tag_id][1] - ALIGN_DATA[1]: # Move forward
#             drone.moveForward()
#             while mag.magnetic[1] < MARKER_DATA[tag_id][1] - ALIGN_DATA[1]:
#                 continue
#             drone.stop()
#             time.sleep(1)
#         # If the y-value of the AprilTag center is in the III or IV quadrant of the detection zone (leaves a +10-pixel buffer)
#         if mag.magnetic[1] > MARKER_DATA[tag_id][1] + ALIGN_DATA[1]: # Move backward
#             drone.moveBackward()
#             while mag.magnetic[1] > MARKER_DATA[tag_id][1] + ALIGN_DATA[1]:
#                 continue
#             drone.stop()
#             time.sleep(1)
#         # If the x-value of the AprilTag center is in the I or IV quadrant of the detection zone (leaves a +10-pixel buffer)
#         if mag.magnetic[0] < MARKER_DATA[tag_id][0] - ALIGN_DATA[0]: # Move right
#             drone.moveRight()
#             while mag.magnetic[0] < MARKER_DATA[tag_id][0] - ALIGN_DATA[0]:
#                 continue
#             drone.stop()
#             time.sleep(1)
#         # If the x-value of the AprilTag center is in the II or III quadrant of the detection zone (leaves a -10-pixel buffer)
#         if mag.magnetic[0] > MARKER_DATA[tag_id][0] + ALIGN_DATA[0]: # Move left
#             drone.moveLeft()
#             while mag.magnetic[0] > MARKER_DATA[tag_id][0] + ALIGN_DATA[0]:
#                 continue
#             drone.stop()
#             time.sleep(1)
# 
#         adjust_altitude(ALIGN_DATA[2], ALIGN_DATA[3])

# Navigates drone between markers
def navigate(camera, detector):
    detection = detect(camera, detector)
    #drone.moveForward()
    #time.sleep(0.5)
    # While there is currently no marker detected
    while len(detection) == 0: # Continue until marker detected
        drone.moveForward()
        time.sleep(1.5)
        drone.stop()
        record_data() # Records a data point to both files
        end_time = time.time() + 5
        while len(detection) == 0 and end_time > time.time():
            detection = detect(camera, detector)
    drone.stop()
    return detection["id"]

# Adjusts drone's altitude
# def adjust_altitude(altitude, threshold):
#     if mag.magnetic[2] < altitude - threshold: # Increase altitude
#         drone.moveUp()
#         while mag.magnetic[2] < altitude - threshold:
#             continue
#         drone.stop()
#         return True
#     elif mag.magnetic[2] > altitude + threshold: # Decrease altitude
#         drone.moveDown()
#         while mag.magnetic[2] > altitude + threshold:
#             continue
#         drone.stop()
#         return True
#     return False

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
        #print("Magnetometer (micro-teslas): X=%4.1f Y=%4.1f Z=%4.1f\n" % (drone.NavData["magneto"][0][0], drone.NavData["magneto"][0][1], drone.NavData["magneto"][0][2]))
        file.write(str(drone.NavData["magneto"][0][0]) + "," + str(drone.NavData["magneto"][0][1]) +"," + str(drone.NavData["magneto"][0][2]) + "\n")
    file.close()
    with open(os.path.join(repository_dir, 'yawData.txt'), 'a') as file:
        angle = drone.NavData["demo"][2][2]
        if angle<0:
            angle+=360
        print("Angle (degrees): " + str(angle))
        file.write(str(angle) + "\n")
    file.close()

# Controls program execution
def main():
    camera = cv2.VideoCapture(0)
    detector = apriltag("tagStandard41h12")
    initialize_files()
    start_drone()
    
    print("Navigating")
    maker_id = navigate(camera, detector)
 
    # Navigate until last marker found and aligned with
    while maker_id != LAST_MARKER_ID:
        time.sleep(5)
        print("Orienting for next marker")
        orient(maker_id, 4)
        time.sleep(10)
        print("Navigating")
        maker_id = navigate(camera, detector)

    # Shutdown sequence
    print("Mission accomplished. Landing.")
    drone.shutdown()
    print("Done")

main()
