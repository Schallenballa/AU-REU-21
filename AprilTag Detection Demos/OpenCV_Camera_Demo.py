import cv2
import numpy as np

#This will open the camera using the OpenCV library (imported as cv2)
camera = cv2.VideoCapture(0)

#This program will run until you hit the ESCAPE KEY
while cv2.waitKey(1) != 0x1b:
    ret, img = camera.read()
    image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imshow("IMG", img)
cv2.destroyAllWindows()
