import numpy as np
import cv2
import preprocess as pp
from transform import four_point_transform


# Scale the scanned image
def resize_image(image):
    min_side = image.shape[0]
    max_size = 1000
    scale_f = max_size / min_side
    resized_img = cv2.resize(image,
                             (int(image.shape[1] * scale_f),
                              int(image.shape[0] * scale_f)),
                             interpolation=cv2.INTER_AREA)
    return resized_img


# Split the image in top half and bottom half
def splitHalf(image):
    startTopH = 50
    half_h = 500
    startBottomH = 550
    top_half = image[startTopH:half_h]
    bottom_half = image[startBottomH:]
    return top_half, bottom_half


# Compute epsilon to add padding on the side of cropped image
# This needs to be updated.
def computeEps(w, h):
    area = w * h
    if area <= 150000:
        return 20


# Detect cards in the image.
# Returns the original image with cards highlighted, along with individual crops saved in the cropped_dict dictionary.
def detectCards(image):
    toWarp = image.copy()
    cropped_dict = dict()
    adjusted = pp.histogram_adjust(image.copy())
    segmented = pp.segmentation(adjusted)
    contours, hierarchy = cv2.findContours(np.uint8(segmented),
                                           cv2.RETR_CCOMP,
                                           cv2.CHAIN_APPROX_SIMPLE)
    contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)
    hull_list = []
    for cnt in contours_sorted[:10]:
        hull = cv2.convexHull(cnt)
        x, y, w, h = cv2.boundingRect(hull)
        if pp.isCardRect(x, y, w, h, hull_list):
            hull_list.append(hull)
            img_box = cv2.rectangle(image, (x, y), (x + w, y + h), color=(0, 255, 0), thickness=2)
            eps = computeEps(w, h)
            rect_point = np.array([[x - eps, y - eps],
                                   [x + w + eps, y - eps],
                                   [x + w + eps, y + h + eps],
                                   [x - eps, y + h + eps]])
            warped = four_point_transform(toWarp, rect_point)
            cropped_dict[x-eps] = warped
    return cropped_dict, image


# The Autocropper class stores:
# 1. the top half and bottom half of the original image with cards highlighted in the list "detected."
# 2. Individual crops of each image are stored in the list "cropped," and sorted by their starting coordinates.
class Autocropper:
    def __init__(self, image):
        self.original_image = image
        self.resized_image = resize_image(image)
        self.topHalf, self.bottomHalf = splitHalf(self.resized_image)
        self.detected = []
        self.cropped = []

        cropped, detected = detectCards(self.topHalf)
        for i in sorted(cropped.keys()):
            cropped[i] = cv2.cvtColor(cropped[i], cv2.COLOR_BGR2RGB)
            self.cropped.append(cropped[i])
        detected = cv2.cvtColor(detected, cv2.COLOR_BGR2RGB)
        self.detected.append(detected)

        cropped, detected = detectCards(self.bottomHalf)
        for i in sorted(cropped.keys()):
            cropped[i] = cv2.cvtColor(cropped[i], cv2.COLOR_BGR2RGB)
            self.cropped.append(cropped[i])
        detected = cv2.cvtColor(detected, cv2.COLOR_BGR2RGB)
        self.detected.append(detected)



