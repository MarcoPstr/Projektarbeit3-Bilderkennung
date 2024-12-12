import cv2 as cv
import numpy as np
import xml.etree.ElementTree as ET

h_l, s_l, v_l, h_h, s_h, v_h = 0, 0, 0, 0, 0, 0


def colorcalibration():
    print("Farbkalibrierung erfolgreich gestartet!")
    cam = cv.VideoCapture(0)

    while cam.isOpened():
        colorList = []
        global h_l, s_l, v_l, h_h, s_h, v_h

        filetree = ET.parse('./colors.xml')
        fileroot = filetree.getroot()

        # Bekannte Farben einlesen
        i = 1
        for element in fileroot:
            colorList.append(f"{i} {element.tag}")
            i += 1

        inp = input(f"Folgende Farben liegen vor:\n" + '\n'.join(colorList) +
                    "\n\nWählen Sie eine der Farben aus um sie zu bearbeiten oder zu löschen\n"
                    "Wenn eine neue Farbe angelegt werden soll drücken Sie \'n\'\n"
                    "Zum Beenden der Kalibrierung drücken Sie \'c\'\n\n")

        if str.lower(inp) == 'c':
            break
        elif str.lower(inp).isnumeric():
            # Eine Farbe wurde gewählt
            inp2 = input(
                f"Sie haben gewählt: {colorList[int(inp) - 1]}\n\nWählen Sie eine Option:\n1\tLöschen\n2\tAnzeigen\n\n")
            selectedElement = fileroot.find(str.split(colorList[int(inp) - 1], " ")[1])
            if inp2 == "1":
                # Farbe löschen
                fileroot.remove(selectedElement)
                filestr = ET.tostring(fileroot, encoding='utf8').decode('utf8')
                filestr = filestr.replace('><', '>\n<')
                with open("./colors.xml", "w") as file:
                    file.write(filestr)
                print("Löschen erfolgreich!")
                continue
            elif inp2 == "2":
                # Farbe anzeigen
                print(f"{colorList[int(inp) - 1]} wird angezeigt.")
                while True:
                    res, image = cam.read()
                    assert res
                    imgHSV = cv.cvtColor(image, cv.COLOR_BGR2HSV)

                    # Obere und Untere Grenzen extrahieren
                    color_lower = np.array(list(map(int, selectedElement.find('lower').text.split(', '))))
                    color_upper = np.array(list(map(int, selectedElement.find('upper').text.split(', '))))
                    
                    # Farbmaske anwenden und optimieren
                    mask = cv.inRange(imgHSV, color_lower, color_upper)
                    kernel = np.ones((25, 25), np.uint8)
                    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel, iterations=1)

                    cv.imshow("image", image)
                    cv.imshow(f"{colorList[int(inp) - 1]} mask", mask)

                    k = cv.waitKey(1)
                    if k == ord('c'):
                        cv.destroyAllWindows()
                        break
                continue
            else:
                print("Keine gültige Eingabe!")
                continue

        elif str.lower(inp) == 'n':
            # Neue Farbe anlegen
            colorPixel = []

            def coloratpx(event, x, y, flags, param):
                global h_l, s_l, v_l, h_h, s_h, v_h
                if event == cv.EVENT_LBUTTONDOWN:
                    h_l, s_l, v_l = 256, 256, 256
                    h_h, s_h, v_h = -256, -256, -256
                    imgHSV = cv.cvtColor(param, cv.COLOR_BGR2HSV)
                    colorPixel.append(imgHSV[y, x])

                    for c in colorPixel:
                        h = c[0]
                        s = c[1]
                        v = c[2]
                        if h < h_l:
                            h_l = h
                        if h > h_h:
                            h_h = h
                        if s < s_l:
                            s_l = s
                        if s > s_h:
                            s_h = s
                        if v < v_l:
                            v_l = v
                        if v > v_h:
                            v_h = v
                    s_l -= 15
                    cv.add(np.uint8([s_h]), np.uint8([15]))
                    v_l -= 15
                    cv.add(np.uint8([v_h]), np.uint8([15]))
            
            #i = 0
            while True:
                res, image = cam.read()
                assert res
                cv.imshow("image", image)
                # Beim Klicken coloratpx aufrufen
                cv.setMouseCallback("image", coloratpx, image)
        
                imgHSV = cv.cvtColor(image, cv.COLOR_BGR2HSV)
                if h_h - h_l > 170:  # Rot Ausnahme
                    mask = cv.inRange(imgHSV, np.array([0, s_l, v_l]), np.array([5, s_h, v_h]))
                else:
                    mask = cv.inRange(imgHSV, np.array([h_l, s_l, v_l]), np.array([h_h, s_h, v_h]))
                kernel = np.ones((25, 25), np.uint8)
                mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel, iterations=1)
                cv.imshow("mask", mask)
                #cv.imwrite(f"./colorspics/{i}mask.png", mask)
                #cv.imwrite(f"./colorspics/{i}.png", image)    
                #i=i+1            

                k = cv.waitKey(1)
                if k == ord('c'):
                    cv.destroyAllWindows()
                    print(f"{h_l}, {s_l}, {v_l}")
                    colorname = input(
                        "Soll die Farbe gespeichert werden? Falls nein schreiben Sie 'n'. Falls ja geben Sie den Namen der Farbe an:\n")

                    if colorname == 'n':
                        colorPixel = []
                        break

                    filetree = ET.parse('./colors.xml')
                    fileroot = filetree.getroot()

                    if fileroot.find(colorname) is not None:
                        inp = input("Diese Farbe ist bereits gespeichert, soll die alte Farbe ueberschrieben werden? (Y/N) ")
                        if inp.lower() != "y":
                            break
                        fileroot.remove(fileroot.find(colorname))

                    colorelement = ET.SubElement(fileroot, colorname)
                    ET.SubElement(colorelement, 'lower').text = f"{h_l}, {s_l}, {v_l}"
                    ET.SubElement(colorelement, 'upper').text = f"{h_h}, {s_h}, {v_h}"
                    filestr = ET.tostring(fileroot, encoding='utf8').decode('utf8')
                    filestr = filestr.replace('><', '>\n<')
                    with open("./colors.xml", "w") as file:
                        file.write(filestr)

                    colorPixel = []
                    h_l, s_l, v_l = 256, 256, 256
                    h_h, s_h, v_h = -1, -1, -1
                    break
            continue

# Gibt Farbmasken zu einem Bild zurück
def findcontoursincolor(image):
    resultList = []
    imageHSV = cv.cvtColor(image, cv.COLOR_BGR2HSV)  

    colors = []
    filetree = ET.parse('./colors.xml')
    fileroot = filetree.getroot()
    
    for color in fileroot:
        colorName = color.tag
        color_lower = np.array(list(map(int, color.find('lower').text.split(', '))))
        color_upper = np.array(list(map(int, color.find('upper').text.split(', '))))
        colors.append([colorName, color_lower, color_upper])

        mask = cv.inRange(imageHSV, color_lower, color_upper)
        kernel = np.ones((25, 25), np.uint8)
        mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel, iterations=1)
        resultList.append([colorName, mask])
    return resultList
