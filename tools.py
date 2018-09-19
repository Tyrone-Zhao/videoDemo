# coding=utf-8
import cv2


def denoise(src, types):
    # cv2.fastNlMeansDenoising() - works with a single grayscale images
    # cv2.fastNlMeansDenoisingColored() - works with a color image.
    # cv2.fastNlMeansDenoisingMulti() - works with image sequence captured in short period of time (grayscale images)
    # cv2.fastNlMeansDenoisingColoredMulti() - same as above, but for color images.
    if types == 'Guassian':
        # Model metrix size and auto diviation
        img = cv2.GaussianBlur(src, (5, 5), 0)
    elif types == 'median':
        img = cv2.medianBlur(src, 5)
    elif types == 'Bilatrial':
        img = cv2.bilateralFilter(src, 9, 75, 75)
    elif types == 'low_pass':
        img = cv2.blur(src, (5, 5))
    else:
        img = src
    return img


def nothing(emp):
    pass
