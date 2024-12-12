import cv2 as cv
import numpy as np

def calibratePX2MMfactor():
    chessboardSize = (9, 6)
    chessboardSquareSize = 25  # in mm
    terminationCriteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    cam = cv.VideoCapture(0)
    _, image = cam.read()
    cam.release()

    grayIMG = cv.cvtColor(image, cv.COLOR_BGR2GRAY) 
    ret, corners = cv.findChessboardCorners(grayIMG, chessboardSize, None)
    corners = cv.cornerSubPix(grayIMG, corners, (11, 11), (-1, -1), terminationCriteria)
    cv.drawChessboardCorners(image, chessboardSize, corners, ret)

    dists = []
    for i in range(chessboardSize[0]-1):
        dist = np.linalg.norm(corners[i+1][0] - corners[i][0])
        dists.append(dist)
        cv.circle(image, (int(corners[i][0][0]), int(corners[i][0][1])), 2, (0, 255, 0), 10)

    f = chessboardSquareSize / np.mean(dists)

    # Faktor speichern
    cv_file = cv.FileStorage('calibration.xml', cv.FILE_STORAGE_WRITE)

    cv_file.write('calibrationFactor', f)

    cv_file.release()

def cvtPX2MM(px):
    cv_file = cv.FileStorage()
    cv_file.open('calibration.xml', cv.FileStorage_READ)

    f = cv_file.getNode('calibrationFactor').real()

    return px * f
    
def cvtMM2PX(mm):
    cv_file = cv.FileStorage()
    cv_file.open('calibration.xml', cv.FileStorage_READ)

    f = cv_file.getNode('calibrationFactor').real()

    return mm / f
