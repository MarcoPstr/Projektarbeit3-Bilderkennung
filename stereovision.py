import cv2 as cv
import colors
import cameracalibration as cc
import triangulation
import robot
import time
import shapes
import numpy as np

def finddepth(cam):
    
    # cam.set(28, 30)

    B = 5            # Distance between cameras [cm]
    f = 4.5           # Focal length [mm]
    alpha = 45      # FOV in horisontal plane [°]

    # Nach Links bewegen
    robot.move(x=-(B*5))
    time.sleep(1)
    cam = cv.VideoCapture(0)
    retL, frame_left = cam.read()
    cam.release()
    time.sleep(1)
    
    # Nach Rechts bewegen
    robot.move(x=(B*10))
    time.sleep(1)
    cam = cv.VideoCapture(0)
    retR, frame_right = cam.read()
    cam.release()
    time.sleep(1)
    
    # Zurück in die Mitte
    robot.move(x=-(B*5))

    height, width = frame_left.shape[:2]  
    
    # Bilder zuschneiden
    frame_left = frame_left[int(height/4):int(height*3/4), :] 
    frame_right = frame_right[int(height/4):int(height*3/4), :]
    #cv.imwrite("./stereorightcrop.png", frame_right) 

    # Mittelpunkte finden
    colorspotsL = colors.findcontoursincolor(frame_left)
    colorspotcentersL = shapes.getColorsCenter(colorspotsL) 
    # Nach Distanz zum erwarteten Mittelpunkt sortieren -> Erster ist der gesuchte
    colorspotcentersL = sorted(colorspotcentersL, key=lambda x: np.abs(x[0]-width/2) - cc.cvtMM2PX(B*5))
    cv.circle(frame_left, colorspotcentersL[0], 1, (0, 0, 0), 3)

    colorspotsR = colors.findcontoursincolor(frame_right)
    colorspotcentersR = shapes.getColorsCenter(colorspotsR)
    # Nach Distanz zum erwarteten Mittelpunkt sortieren -> Erster ist der gesuchte
    colorspotcentersR = sorted(colorspotcentersR, key=lambda x: np.abs(x[0]-width/2) + cc.cvtMM2PX(B*5))
    cv.circle(frame_right, colorspotcentersR[0], 1, (0, 0, 0), 3)
            
    cv.imshow("left eye", frame_left)
    cv.imshow("right eye", frame_right)
    cv.waitKey(3000)
    cv.destroyAllWindows()

    depth = triangulation.find_depth(colorspotcentersR[0], colorspotcentersL[0], frame_right, frame_left, B, f, alpha)
    
    return depth


