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

import cv2
from pytesseract import image_to_string
from PIL import Image


#TEST_IMAGE_PATH = 'res/img/P6070001.jpg'
TEST_IMAGE_PATH = 'res/img/P1010005.jpg'

# loading
img = cv2.imread(TEST_IMAGE_PATH)
#img = cv2.medianBlur(img,5)

img_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
cv2.blur(img_gray, (5,5), img)

# plate localization
ret, threshed = cv2.threshold(img_gray, 127, 255, cv2.THRESH_OTSU)
threshedcopy = threshed.copy()
_, contours, _ = cv2.findContours(threshedcopy, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

#TODO Think how remove small contours
contours = [c for c in contours if cv2.contourArea(c) > 1000]
#TODO what if the there are many rectangles

plateContour = 0
for c in contours:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    if len(approx) == 4:
        plateContour = approx
        break

color = (0,255,0)
cv2.drawContours(img, [plateContour], -1, color, thickness=2)
#cv2.drawContours(img, contours, -1, color, thickness=2)

x,y,w,h = cv2.boundingRect(plateContour)
crop = img[y:y+h,x:x+w]

# OCR part
cv2.imshow('img', img)
cv2.imwrite('im.jpg', crop)
im = Image.open(r'im.jpg')

print(image_to_string(im))
cv2.waitKey(0)
cv2.destroyAllWindows()