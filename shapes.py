import cv2 as cv
import numpy as np
import colors
import robot
import cameracalibration

def getColorsCenter(masks):
    centers = []   
    for colorspot in masks:
        colorMask = colorspot[1]
        image = cv.cvtColor(colorMask, cv.COLOR_GRAY2BGR)
        # Konturen finden
        contours, _ = cv.findContours(colorMask, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)        
        for contour in contours:
            M = cv.moments(contour)  # mech. Momente
            if M['m00'] > 2000:
                cv.drawContours(image, contour, -1, (255, 0, 0), 3)
                cx = int(M['m10'] / M['m00'])  # Mittelpunktberechnung
                cy = int(M['m01'] / M['m00'])
                centers.append([cx, cy])
            else:
                # Kontur zu klein -> nicht beachten
                continue
    return centers


def findshapes():
    cam = cv.VideoCapture(0)
    while True:
        result, image = cam.read()
        cam.release()
        height, width = image.shape[:2]
        cx, cy, pitch = 0, 0, 0
        resultList = colors.findcontoursincolor(image)
        # Initialisierung Rückgabewerte
        foundcolor = ""
        foundshape = ""
        foundcenter = []

        for object in resultList:
            color = object[0]
            colormask = object[1]
            cv.imshow("mask", colormask)
            cv.waitKey(1)
            # Konturen finden
            contours, _ = cv.findContours(colormask, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
            for contour in contours:
                M = cv.moments(contour)  # mech. Momente
                if M['m00'] > 2000:
                    cx = int(M['m10'] / M['m00'])  # Mittelpunktberechnung
                    cy = int(M['m01'] / M['m00'])
                    if np.abs(cy-height/2) > 50 or np.abs(cx-width/2) > 50:
                        # Erwartung: Mittelpunkt liegt nah an Bildmitte n.e.
                        continue
                    foundcenter = [cx, cy]
                    cv.circle(image, (cx, cy), 1, (0, 0, 0), 4)  # Mittelpunkt markieren
                    cv.drawContours(image, contour, -1, (255, 0, 0), 3)
                else:
                    # Zu klein -> Nicht beachten
                    continue

                # Kreis Detection
                binarydetectionmapcircle = cv.blur(colormask, (7, 7))
                rows = binarydetectionmapcircle.shape[0]
                circles = cv.HoughCircles(binarydetectionmapcircle, cv.HOUGH_GRADIENT, 1.1, rows / 8,
                                          param1=50, param2=40,
                                          minRadius=10, maxRadius=300)

                center = (0, 0)
                radius = 0

                if circles is not None:
                    # Kreis gefunden
                    foundcolor = color
                    circles = np.uint16(np.around(circles))
                    for i in circles[0, :]:
                        center = (i[0], i[1])
                        if np.abs(i[0]-width/2) > 50 or np.abs(i[1]-height/2) > 50:
                            # Erwartung: Mittelpunkt liegt nah an Bildmitte n.e.
                            continue
                        radius = i[2]
                        cv.circle(image, center, radius, (255, 0, 255), 3)
                        # Auf Bild ergebnis plotten
                        xn = np.uint16(i[0] + np.round(1.1 * i[2]))
                        cv.putText(image, color + ' Circle', (xn, i[1]), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        foundshape = "circle"

                colormaskBGR = cv.cvtColor(colormask, cv.COLOR_GRAY2BGR)
                colormaskBGR = cv.drawContours(colormaskBGR, contour, -1, (0, 255, 0), 6)
                cv.imshow(color + " mask", colormaskBGR)

                # Polygon Detection wenn kein kreis da ist oder alle kreise zu weit entfernt sind
                if circles is None or \
                        (circles is not None and (center[0] + radius < cx > center[0] - radius)
                         or (center[0] + radius > cx < center[0] - radius)):
                    
                    # Punkte approximieren
                    approx = cv.approxPolyDP(contour, 0.025 * cv.arcLength(contour, True), True)

                    x1, y1 = contour[0][0]
                    if len(approx) == 4:
                        # Viereck
                        # Rechtwinkligkeit prüfen
                        u = approx[0, 0] - approx[1, 0]
                        v = approx[1, 0] - approx[2, 0]

                        alpha = np.arccos((u[0] * v[0] + u[1] * v[1]) / (
                                    (np.sqrt(np.square(u[0]) + np.square(u[1]))) * (
                                np.sqrt(np.square(v[0]) + np.square(v[1])))))

                        if np.abs(alpha - (np.pi / 2)) < 0.1:  # 90 Grad zwischen den Parallelen
                            x, y, w, h = cv.boundingRect(contour)
                            ratio = float(w) / h
                            # Seitenverhältnis prüfen
                            if 0.93 <= ratio <= 1.07:
                                image = cv.drawContours(image, [contour], -1, (0, 255, 255), 3)
                                cv.putText(image, color + ' Square', (x1, y1), cv.FONT_HERSHEY_SIMPLEX, 0.6,
                                           (255, 255, 0), 2)
                                foundshape = "square"
                            else:
                                cv.putText(image, color + ' Rectangle', (x1, y1), cv.FONT_HERSHEY_SIMPLEX, 0.6,
                                           (0, 255, 0), 2)
                                image = cv.drawContours(image, [contour], -1, (0, 255, 0), 3)
                                foundshape = "rectangle"
        
                    elif len(approx) == 6:
                        # Hexagon
                        image = cv.drawContours(image, [contour], -1, (255, 255, 0), 3)
                        cv.putText(image, color + ' Hexagon', (x1, y1), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                        foundshape = "hexagon"
                    elif len(approx) == 8:
                        # Oktagon
                        image = cv.drawContours(image, [contour], -1, (255, 0, 0), 3)
                        cv.putText(image, color + ' Octagon', (x1, y1), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                        foundshape = "octagon"

                    # Winkel zur Vertikalen berechnen
                    # Punkte nach x-Koordinate sortieren
                    sorted_points = sorted(approx, key=lambda x: x[0, 0])
                    mostleft_points = sorted_points[:2]
                    p1 = mostleft_points[0][0]
                    p2 = mostleft_points[1][0]
                    cv.circle(image, p1, 2, (0,255,0), -1)
                    cv.circle(image, p2, 2, (0,255,0), -1)
                    dx = p1[0] - p2[0]
                    dy = p1[1] - p2[1]
                    beta = (np.arctan2(np.abs(dx), -dy)/np.pi*180)
                    # Winkel in [-45 45] für Gripper konvertieren
                    if beta > 90:
                        pitch = 180 - beta
                    elif beta > 45:
                        pitch = 90 - beta
                    else:
                        pitch = -beta
                    foundcolor = color

        cv.imshow("original image", image)
        cv.imwrite("./foundshape.png", image)
        cv.waitKey(3000)
        cv.destroyAllWindows()
        
        return [pitch, foundcolor, foundshape, foundcenter]
