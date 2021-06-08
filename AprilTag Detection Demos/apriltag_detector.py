from picamera import PiCamera
from time import sleep
import cv2
import numpy as np
from apriltag import apriltag

camera = PiCamera()

camera.start_preview()
sleep(5)
camera.capture('/home/pi/Desktop/image.jpg')
camera.stop_preview()

imagepath = '/home/pi/Desktop/image.jpg'
image = cv2.imread(imagepath, cv2.IMREAD_GRAYSCALE)
detector = apriltag("tagStandard41h12")

detections = detector.detect(image)

print(detections, "\n", Image(imagepath).size())
