import cv2
import numpy as np
from apriltag import apriltag

COLOR1 = 112, 132, 58 #BGR
COLOR2 = 0, 0, 255 #BGR
COLOR3 = 240, 105, 0 #BGR
MAXWIDTH = 640
MAXHEIGHT = 480
camera = cv2.VideoCapture(0)
#The picture is 640 x 480
#CENTER = (320, 240)
#The AprilTag detects widthxheight
camera2 = camera
detector = apriltag("tagStandard41h12")





def arrayLines():
    while cv2.waitKey(1) != 0x1b:
        ret, img = camera.read()
        image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        #Defines initial values of variables
        WIDTH = 64
        HEIGHT = 48
        COORDINATES = []
        COUNT = 0
        PRIMED = False
        LB = [0, 0]
        RB = [0, 0]
        RT = [0, 0]
        LT = [0, 0]
        CNT = [0, 0]
        
        #Creates the variables which indicate a detection
        detections = detector.detect(image)
        for det in detections:
                if det["margin"] >= 10:
                   rect = det["lb-rb-rt-lt"].astype(int).reshape((-1, 1, 2))
                   cv2.polylines(img, [rect], True, COLOR1, 4)
                   ident = str(det["id"])
                   pos = det["center"].astype(int) + (-10, 10)
                   cv2.putText(img, ident, tuple(pos), cv2.FONT_HERSHEY_SIMPLEX, 1, COLOR1, 2)
                   LB = det["lb-rb-rt-lt"][0]
                   RB = det["lb-rb-rt-lt"][1]
                   RT = det["lb-rb-rt-lt"][2]
                   LT = det["lb-rb-rt-lt"][3]
                   CNT = det["center"].astype(int)
                   
        
        #Loops through some math to create the COORDINATES[][] array to store the 4 vertices and boolean of whether or not a detection point is closeby
        for x in range(9):
            for y in range(9):
                HEIGHTCHECK1 = HEIGHT - 25
                HEIGHTCHECK2 = HEIGHT + 25
                WIDTHCHECK1 = WIDTH - 25
                WIDTHCHECK2 = WIDTH + 25
                if (HEIGHTCHECK1 < int(LB[1])) and (HEIGHTCHECK2 > int(LB[1])) and (WIDTHCHECK1 < int(LB[0])) and (WIDTHCHECK2 > int(LB[0])):
                    PRIMED = True
                elif (HEIGHTCHECK1 < int(RB[1])) and (HEIGHTCHECK2 > int(RB[1])) and (WIDTHCHECK1 < int(RB[0])) and (WIDTHCHECK2 > int(RB[0])):
                    PRIMED = True
                elif (HEIGHTCHECK1 < int(RT[1])) and (HEIGHTCHECK2 > int(RT[1])) and (WIDTHCHECK1 < int(RT[0])) and (WIDTHCHECK2 > int(RT[0])):
                    PRIMED = True
                elif (HEIGHTCHECK1 < int(LT[1])) and (HEIGHTCHECK2 > int(LT[1])) and (WIDTHCHECK1 < int(LT[0])) and (WIDTHCHECK2 > int(LT[0])):
                    PRIMED = True
                COORDINATES.append([WIDTH,HEIGHT,PRIMED])
                HEIGHT = HEIGHT + 48
                COUNT = COUNT + 1
                PRIMED = False
            WIDTH = WIDTH + 64
            HEIGHT = 48

        #Runs a loop to generate all of the rectangles and assigns the color based on detection of fiducial corner
        xCOUNT = 0
        for x in range(8):
            for y in range(8):
                rect = np.array([[COORDINATES[xCOUNT][0],COORDINATES[xCOUNT][1]], [COORDINATES[xCOUNT+9][0], COORDINATES[xCOUNT+9][1]], [COORDINATES[xCOUNT+10][0], COORDINATES[xCOUNT+10][1]], [COORDINATES[xCOUNT+1][0], COORDINATES[xCOUNT+1][1]]], np.int32)
                if (COORDINATES[xCOUNT][2] == 1):
                    cv2.polylines(img, [rect], True, COLOR2, 2)
                elif (COORDINATES[xCOUNT+9][2] == 1):
                    cv2.polylines(img, [rect], True, COLOR2, 2)
                elif (COORDINATES[xCOUNT+10][2] == 1):
                    cv2.polylines(img, [rect], True, COLOR2, 2)
                elif (COORDINATES[xCOUNT+1][2] == 1):
                    cv2.polylines(img, [rect], True, COLOR2, 2)
                else:
                    cv2.polylines(img, [rect], True, COLOR1, 1)
                xCOUNT = xCOUNT + 1
            xCOUNT = xCOUNT + 1

        if CNT[0] != 0:
            line = np.array([(320,240), CNT], np.int32)
            cv2.polylines(img, [line], False, COLOR3, 3)
        cv2.imshow("IMG", img)
    cv2.destroyAllWindows()


#Old function which will hardcode all of the lines over the display
def hardCodedLines():
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

        #detections = detector.detect(image)
        #for det in detections:
        #        if det["margin"] >= 10:
        #           rect = det["lb-rb-rt-lt"].astype(int).reshape((-1, 1, 2))
        #           cv2.polylines(img, [rect], True, COLOR1, 4)
        #           ident = str(det["id"])
        #           pos = det["center"].astype(int) + (-10, 10)
        #           cv2.putText(img, ident, tuple(pos), cv2.FONT_HERSHEY_SIMPLEX, 1, COLOR1, 2)







        cv2.imshow("IMG", img)
        #print(detections)

    cv2.destroyAllWindows()

arrayLines()
