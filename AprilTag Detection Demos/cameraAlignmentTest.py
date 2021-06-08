import cv2
import numpy as np
from apriltag import apriltag

COLOR1 = 112, 132, 58 #BGR
COLOR2 = 0, 0, 255 #BGR

camera = cv2.VideoCapture(0)
camera2 = camera
detector = apriltag("tagStandard41h12")

while cv2.waitKey(1) != 0x1b:
    ret, img = camera.read()
    image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detections = detector.detect(image)
    #for det in detections:
    #        if det["margin"] >= 10:
    #           rect = det["lb-rb-rt-lt"].astype(int).reshape((-1, 1, 2))
    #           cv2.polylines(img, [rect], True, COLOR1, 2)
    #           ident = str(det["id"])
    #           pos = det["center"].astype(int) + (-10, 10)
    #           cv2.putText(img, ident, tuple(pos), cv2.FONT_HERSHEY_SIMPLEX, 1, COLOR2, 2)              
    cv2.imshow("IMG", img)

    #print(detections)

cv2.destroyAllWindows()
