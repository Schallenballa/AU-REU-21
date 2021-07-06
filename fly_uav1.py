import time
import signal
import cv2
from apriltag import apriltag
import ps_drone
import os
import math

# ID of last marker in the course
LAST_MARKER_ID = 1
# Known vlaue of the yaw needed for a path to the next marker.
# The position of each data member corresponds with the marker ID.
MARKER_DATA = (70, 90)

drone = ps_drone.Drone()

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
    print("Moving up")
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
        print(detection, "\n\nEnding detection. Marker detected...", detection[0])
        return detection[0]
    print(detection, "\n\nEnding detection...")
    return detection

# Orients yaw of drone to yaw needed for path to the next marker
def orient(tag_id):
    yaw_needed = MARKER_DATA[tag_id]
    print("Yaw needed: ", yaw_needed)
    drone.turnAngle(yaw_needed, 1)
    print("Finished turning...")

# Navigates drone between markers
def navigate(previous_id, camera, detector):
    detection = detect(camera, detector)
    # While there is currently no marker detected
    while len(detection) == 0 or detection["id"] == previous_id: # Continue until new marker detected
        print("Moving forward...")
        drone.moveForward()
        time.sleep(1.5)
        drone.stop()
        record_data() # Records a data point to both files
        end_time = time.time() + 5
        while len(detection) == 0 and end_time > time.time():
            detection = detect(camera, detector)
    print("Done moving forward...")
    drone.stop()
    return detection["id"]

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
    maker_id = navigate(-1, camera, detector)

    # Navigate until last marker found and aligned with
    while maker_id != LAST_MARKER_ID:
        time.sleep(5)
        print("Orienting for next marker")
        orient(maker_id)
        time.sleep(10)
        print("Navigating")
        maker_id = navigate(marker_id, camera, detector)
        print("New, previous marker detected: " + str(maker_id))

    # Shutdown sequence
    print("Mission accomplished. Landing.")
    drone.shutdown()
    print("Done")

main()
