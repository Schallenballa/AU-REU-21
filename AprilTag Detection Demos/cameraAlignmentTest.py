import cv2
import numpy as np
from apriltag import apriltag

COLOR1 = 112, 132, 58 #BGR
COLOR2 = 0, 0, 255 #BGR

camera = cv2.VideoCapture(0)
#The picture is 640 x 480
#CENTER = (320, 240)
camera2 = camera
detector = apriltag("tagStandard41h12")

while cv2.waitKey(1) != 0x1b:
    ret, img = camera.read()
    image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    
    
    #Vertical Lines
    linesv0 = np.array([[0,0], [0,480]], np.int32)
    linesv1 = np.array([[64,0], [64,480]], np.int32)
    linesv2 = np.array([[128,0], [128,480]], np.int32)
    linesv3 = np.array([[192,0], [192,480]], np.int32)
    linesv4 = np.array([[256,0], [256,480]], np.int32)
    linesv5 = np.array([[320,0], [320,480]], np.int32)
    linesv6 = np.array([[384,0], [384,480]], np.int32)
    linesv7 = np.array([[448,0], [448,480]], np.int32)
    linesv8 = np.array([[512,0], [512,480]], np.int32)
    linesv9 = np.array([[576,0], [576,480]], np.int32)
    linesv9 = np.array([[576,0], [576,480]], np.int32)
    linesv10 = np.array([[640,0], [640,480]], np.int32)
    
    cv2.polylines(img, [linesv0], False, COLOR2, 1)
    cv2.polylines(img, [linesv1], False, COLOR2, 1)
    cv2.polylines(img, [linesv2], False, COLOR2, 1)
    cv2.polylines(img, [linesv3], False, COLOR2, 1)
    cv2.polylines(img, [linesv4], False, COLOR2, 1)
    cv2.polylines(img, [linesv5], False, COLOR2, 1)
    cv2.polylines(img, [linesv6], False, COLOR2, 1)
    cv2.polylines(img, [linesv7], False, COLOR2, 1)
    cv2.polylines(img, [linesv8], False, COLOR2, 1)
    cv2.polylines(img, [linesv9], False, COLOR2, 1)
    cv2.polylines(img, [linesv10], False, COLOR2, 1)
    
    
    #Horizontal Lines
    linesh0 = np.array([[0,0], [640,0]], np.int32)
    linesh1 = np.array([[0,48], [640,48]], np.int32)
    linesh2 = np.array([[0,96], [640,96]], np.int32)
    linesh3 = np.array([[0,144], [640,144]], np.int32)
    linesh4 = np.array([[0,192], [640,192]], np.int32)
    linesh5 = np.array([[0,240], [640,240]], np.int32)
    linesh6 = np.array([[0,288], [640,288]], np.int32)
    linesh7 = np.array([[0,336], [640,336]], np.int32)
    linesh8 = np.array([[0,384], [640,384]], np.int32)
    linesh9 = np.array([[0,432], [640,432]], np.int32)
    linesh10 = np.array([[0,480], [640,480]], np.int32)
    
    cv2.polylines(img, [linesh0], False, COLOR2, 1)
    cv2.polylines(img, [linesh1], False, COLOR2, 1)
    cv2.polylines(img, [linesh2], False, COLOR2, 1)
    cv2.polylines(img, [linesh3], False, COLOR2, 1)
    cv2.polylines(img, [linesh4], False, COLOR2, 1)
    cv2.polylines(img, [linesh5], False, COLOR2, 1)
    cv2.polylines(img, [linesh6], False, COLOR2, 1)
    cv2.polylines(img, [linesh7], False, COLOR2, 1)
    cv2.polylines(img, [linesh8], False, COLOR2, 1)
    cv2.polylines(img, [linesh9], False, COLOR2, 1)
    cv2.polylines(img, [linesh10], False, COLOR2, 1)
    
    
    #Center square
    square1 = np.array([[288,216],[352,216],[352,264],[288,264]], np.int32)
    cv2.polylines(img, [square1], True, COLOR1, 2)
    
    detections = detector.detect(image)
    for det in detections:
            if det["margin"] >= 10:
               rect = det["lb-rb-rt-lt"].astype(int).reshape((-1, 1, 2))
               cv2.polylines(img, [rect], True, COLOR1, 4)
               ident = str(det["id"])
               pos = det["center"].astype(int) + (-10, 10)
               cv2.putText(img, ident, tuple(pos), cv2.FONT_HERSHEY_SIMPLEX, 1, COLOR1, 2)
    
    
    
    
    
    
    
    cv2.imshow("IMG", img)
    print(detections)

cv2.destroyAllWindows()
