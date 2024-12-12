import cv2 as cv
import cameracalibration
import colors
import stereovision
import shapes
import triangulation
import numpy as np

import robot
import time

def main():
    # Start Console
    mode = input(f"Bitte wählen Sie den Modus in dem die Anwendung gestartet werden soll:"
                 f"\n\n1\tStereo Calibration\n2\tFarbkalibrierung\n3\tRegelanwendung\n\n")
    match str.lower(mode):
        case "1":
            print("Die Kamerakalibrierung wird gestartet...")
            cameracalibration.calibratePX2MMfactor()
            return
        case "2":
            print("Die Farbkalibrierung wird gestartet...")
            colors.colorcalibration()
            return
        case "3":
            print("Die Anwendung wird gestartet...")
            cam = cv.VideoCapture(0)
            _, image = cam.read()
            cam.release()

            height, width = image.shape[:2]
            # "Farbflecken" finden
            colorspots = colors.findcontoursincolor(image)
            
            # Mittelpunkte der "Farbflecken" finden
            colorspotcenters = shapes.getColorsCenter(colorspots)
            
            for center in colorspotcenters:
                # Mittelpunkte markieren
                cv.circle(image, center, 2, (0, 0, 0), -1)

            cv.imshow("Farbkleckse", image)            
            cv.waitKey(3000)  # 3s warten
            cv.destroyAllWindows()
            
            for center in colorspotcenters:
                # Über "Farbfleck" bewegen
                movex = cameracalibration.cvtPX2MM(center[0] - width / 2)
                movey = cameracalibration.cvtPX2MM(center[1] - height / 2)
                robot.move(movex, movey)
                time.sleep(3)
                
                res = shapes.findshapes()                
                
                #Schnellere ungenauere Variante
                #movez = triangulation.find_depth(res[3], center, image, image, np.linalg.norm([movex, movey])/10, 0, 45) 

                #Genaue, langsamere variante
                movez = stereovision.finddepth(cam)
                
                movez = movez * 10 - 125  # Umrechnung in mm und 125mm Kamerabstand zu greifer
                movez = movez * 0.93  # Empirischer Korrekturfaktor

                robot.openGripper()
                robot.move(0, -80, -movez, res[0])  # Runter zum Objekt
                time.sleep(5)
                robot.closeGripper()
                robot.move(0, 0, movez, -res[0])  # Gripper gerade machen und hoch
                robot.sendcolorandshape(res[1], res[2])  # Farb/Form an Steuerung
                time.sleep(3)
                robot.openGripper()
                time.sleep(5)
            return
        case _:
            print("Keine gültige Eingabe gefunden!")
            return

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)


