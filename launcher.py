'''
This program is for getting info from licence plates

Main steps of recognition due to wiki: https://en.wikipedia.org/wiki/Automatic_number_plate_recognition

* Plate localization – responsible for finding and isolating the plate on the picture.
* Plate orientation and sizing – compensates for the skew of the plate and adjusts the dimensions to the required size.
* Normalization – adjusts the brightness and contrast of the image.
* Character segmentation – finds the individual characters on the plates.
* Optical character recognition.
* Syntactical/Geometrical analysis – check characters and positions against country-specific rules.
* The averaging of the recognised value over multiple fields/images to produce a more reliable or confident result.
  Especially since any single image may contain a reflected light flare, be partially obscured or other temporary effect
'''

from os import listdir, path, remove
import sqlite3
import cv2
from pytesseract import image_to_string
from PIL import Image


RES_FOLDER_PATH = 'res/img/'
COLOR = (0, 255, 0)

positive_cnt = 0
negative_cnt = 0

def load_file_list():
    conn = sqlite3.connect('plates.sqlite')
    c = conn.cursor()
    c.execute('SELECT filename FROM plates')
    data = [e[0] for e in c.fetchall()]
    # in case you would like to load all files in the folder
    #data = [f for f in listdir(RES_FOLDER_PATH) if path.isfile(path.join(RES_FOLDER_PATH, f)) and f[-4:] == '.jpg']
    return data

def preprocess(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray = cv2.blur(img_gray, (5, 5), img)
    ret, threshed = cv2.threshold(img_gray, 128, 255, cv2.THRESH_OTSU)
    return threshed

def localise_plate(img):
    # plate localization
    _, contours, _ = cv2.findContours(img.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # TODO Think how remove small contours
    contours = [c for c in contours if cv2.contourArea(c) > 1000]
    # TODO what if the there are many rectangles
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            return approx
    return None

def get_plate_value(plateContour, img):
    if plateContour is not None:
        cv2.drawContours(img, [plateContour], -1, COLOR, thickness=2)
        x, y, w, h = cv2.boundingRect(plateContour)
        crop = img[y:y + h, x:x + w]

        # OCR part
        cv2.imwrite('plate.jpg', crop)
        im = Image.open(r'plate.jpg')
        try:
            str = image_to_string(im)
            print(str)
        except UnicodeDecodeError:
            # TODO solve lib problem
            print("OMFG! Tesseract fail with encoding. Will solve it later.")
        finally:
            remove("plate.jpg")


img_name_list = load_file_list()
for p in img_name_list:
    img = cv2.imread(RES_FOLDER_PATH + p)
    preprocessed_img = preprocess(img)
    plateContour = localise_plate(preprocessed_img)
    get_plate_value(plateContour, img)
    cv2.imshow(p, img)

    key_pressed = cv2.waitKey(0)
    #press esc to quit
    if key_pressed == 27:
        break
    #if you agree, press enter
    elif key_pressed == 13:
        print(p, '+')
        positive_cnt += 1
    #if you disagree, press space
    elif key_pressed == 32:
        print(p, 'x')
        negative_cnt += 1
    else:
        print(p)
    cv2.destroyAllWindows()

cv2.destroyAllWindows()
loc_ration = positive_cnt / (positive_cnt + negative_cnt)
print('Plate localisation ration is {0:.2f}'.format(loc_ration))