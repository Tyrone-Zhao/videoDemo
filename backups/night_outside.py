import cv2
import numpy as np
import funct


outside_cord_arry = [[(375, 266), (453, 245), (431, 473), (360, 511)]]
path = ".\\室外-茅店子-2018_01_21_20_20_21-2018_01_21_21_28_31.avi.avi"


def night_enter(path, start_frm, coordinate):
    cap = cv2.VideoCapture(path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frm)
    mog = cv2.createBackgroundSubtractorMOG2()
    loop_flag = start_frm
    false_cnt = 0
    true_cnt = 0
    while True:
        loop_flag = loop_flag + 1
        ret, img = cap.read()
        if ret == False:
            break
        pts = np.array(coordinate, dtype=np.int32)
        mask = np.zeros((img.shape[0], img.shape[1]))

        cv2.fillConvexPoly(mask, pts, 1)
        mask = mask.astype(np.bool)
        out = np.zeros_like(img)
        out[mask] = img[mask]
        img = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
        img = funct.denoise(img, 'median')
        fgmask = mog.apply(img)
        fgmask = funct.denoise(fgmask, 'median')
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        fgmask = cv2.erode(fgmask, kernel, iterations=1)
        fgmask = cv2.dilate(fgmask, kernel)

        judging = fgmask
        _, contours, hierarchy1 = cv2.findContours(judging, cv2.RETR_TREE,
                                                   cv2.CHAIN_APPROX_SIMPLE)

        cv2.drawContours(img, contours, -1, (0, 0, 0), 3)

        points = 0
        for c in contours:
            points += len(c)
        if points > 200:
            if true_cnt == 1:
                enter = loop_flag
                print("enter = ", enter)
            true_cnt += 1
            false_cnt = 0
        else:
            false_cnt += 1
        if false_cnt > 1500:
            if true_cnt > 0:
                leave = loop_flag
                print("leave = ", leave)
                true_cnt = 0


if __name__ == "__main__":
    night_enter(path, 0, outside_cord_arry[0])
