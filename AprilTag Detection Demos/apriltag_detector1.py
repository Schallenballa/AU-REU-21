import cv2
import numpy as np
from apriltag import apriltag

BLUE = 255, 0, 0

camera = cv2.VideoCapture(0)
detector = apriltag("tagStandard41h12")

while cv2.waitKey(1) != 0x1b:
    ret, img = camera.read()
    image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detections = detector.detect(image)
    for det in detections:
        if det["margin"] >= 10:
           rect = det["lb-rb-rt-lt"].astype(int).reshape((-1, 1, 2))
           cv2.polylines(img, [rect], True, BLUE, 2)
           ident = str(det["id"])
           pos = det["center"].astype(int) + (-10, 10)
           cv2.putText(img, ident, tuple(pos), cv2.FONT_HERSHEY_SIMPLEX, 1, BLUE, 2)
    cv2.imshow("IMG", img)
    print(detections, "\n(Rows, Columns):", image.shape, "\nTotal Pixels:", image.size)
    
cv2.destroyAllWindows()

