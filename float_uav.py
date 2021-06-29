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
    #drone.shutdown()
    exit()

signal.signal(signal.SIGQUIT, exit_gracefully)

def detect(camera, detector):
    print("Starting detection...")
    ret, img = camera.read()
    image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detection = detector.detect(image)
    if len(detection) != 0:
        print("Marker detected!")
        if detection[0]["margin"] >= 10:
       	    rect = detection[0]["lb-rb-rt-lt"].astype(int).reshape((-1, 1, 2))
            cv2.polylines(img, [rect], True, BLUE, 2)
       	    ident = str(detection[0]["id"])
       	    pos = detection[0]["center"].astype(int) + (-10, 10)
       	    cv2.putText(img, ident, tuple(pos), cv2.FONT_HERSHEY_SIMPLEX, 1, BLUE, 2)
            cv2.imshow("IMG", img)
        print(detection, "\n\nEnding detection...")
        return detection[0]
    print(detection, "\n\nEnding detection...")
    return detection

def main():
    camera = cv2.VideoCapture(0)
    detector = apriltag("tagStandard41h12")
    detect(camera, detector)
    cv2.destroyAllWindows()
    print("Done")

main()
