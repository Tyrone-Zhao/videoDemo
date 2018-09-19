#coding=utf-8
import cv2
import math
import time
import numpy as np


# 整合封装opencv中所有去噪函数
def denoise(src, type):
    #cv2.fastNlMeansDenoising() - works with a single grayscale images
    #cv2.fastNlMeansDenoisingColored() - works with a color image.
    #cv2.fastNlMeansDenoisingMulti() - works with image sequence captured in short period of time (grayscale images)
    #cv2.fastNlMeansDenoisingColoredMulti() - same as above, but for color images.
    if type == 'Guassian':
        # Model metrix size and auto diviation
        img = cv2.GaussianBlur(src, (5, 5), 0)
    elif type == 'median':
        img = cv2.medianBlur(src, 5)
    elif type == 'Bilatrial':
        img = cv2.bilateralFilter(src, 9, 75, 75)
    elif type == 'low_pass':
        img = cv2.blur(src, (5, 5))
    return img


# 寻找点集的重心
def poly_center(arr):
    length = arr.shape[0]
    if not length == 0:
        sum_x = np.sum(arr[:, 0])
        sum_y = np.sum(arr[:, 1])
        cx = sum_x / length
        cy = sum_y / length
    else:
        cx = -1
        cy = -1
    return cx, cy


# 判定当前时间是白天还是黑夜
def get_day_night(location_flag, start_ts):
    start_ts = int(start_ts)
    if location_flag == "outside":
        if 8 <= start_ts <= 21:
            day_flag = 1
        else:
            day_flag = 0
    elif location_flag == "inside":
        if 6 <= start_ts <= 17:
            day_flag = 1
        else:
            day_flag = 0
    else:
        day_flag = None
    return day_flag


# 判断两个矩形是否相交
def mat_inter(box1, box2):
    # box=(xA,yA,xB,yB)
    x01, y01, x02, y02 = box1
    x11, y11, x12, y12 = box2
    lx = abs((x01 + x02) / 2 - (x11 + x12) / 2)
    ly = abs((y01 + y02) / 2 - (y11 + y12) / 2)
    sax = abs(x01 - x02)
    sbx = abs(x11 - x12)
    say = abs(y01 - y02)
    sby = abs(y11 - y12)
    if lx <= (sax + sbx) / 2 and ly <= (say + sby) / 2:
        return True
    else:
        return False


# 计算两个矩形框的重合度
def solve_coincide(box1, box2):
    # box=(xA,yA,xB,yB)
    if mat_inter(box1, box2) is True:
        x01, y01, x02, y02 = box1
        x11, y11, x12, y12 = box2
        col = min(x02, x12) - max(x01, x11)
        row = min(y02, y12) - max(y01, y11)
        intersection = col * row
        area1 = (x02 - x01) * (y02 - y01)
        area2 = (x12 - x11) * (y12 - y11)
        smaller = (lambda area1, area2: min(area1, area2))(area1, area2)
        coincide = intersection / smaller
        return coincide
    else:
        return 0


# 判断某一区域是否有人
def if_people(img, mog, bbox):
    img = img[int(bbox[1]):int(bbox[1] + bbox[3]), int(bbox[0]):int(bbox[0] + bbox[2])]
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = denoise(img, 'median')
    fgmask = mog.apply(img)
    fgmask = denoise(fgmask, 'median')

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    fgmask = cv2.erode(fgmask, kernel, iterations=1)
    fgmask = cv2.dilate(fgmask, kernel)

    judging = fgmask
    _, contours, hierarchy1 = cv2.findContours(judging, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cv2.drawContours(img, contours, -1, (0, 0, 0), 3)
    points = 0
    for c in contours:
        points += len(c)
    if points > 200:
        return True
    else:
        return False


#将帧数结合开始时间转化为当前时间
def frametotime(fps, start_time, frames):
    # start_time is a list, include 6 elements
    timestring = ''
    for i in range(len(start_time)):
        timestring = timestring + str(start_time[i]) + '-'

    timestring = timestring[:-1]
    start_time = time.strptime(timestring, "%Y-%m-%d-%H-%M-%S")
    second = int(frames / fps)
    start_time = time.mktime(start_time)
    end_time = start_time + second
    end_time = time.localtime(end_time)
    return end_time


#将时间戳中的小时数提取并输出
def format_time(time_st):
    hour = time_st[3]
    return hour


# 根据日夜情况选定 GMM 算法的阈值
def decide_day(flag):
    if flag == 0:
        threshold = 1000
    else:
        threshold = 800
    return threshold


# 回岗运动趋势的符号判定
def signal(x, y, ix, iy):
    if x - ix > 0:
        horizion = True
    else:
        horizion = False
    if y - iy > 0:
        vertical = True
    else:
        vertical = False
    return horizion, vertical
