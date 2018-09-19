import cv2
import numpy as np
from tools import denoise
from tools import nothing
import argparse


def glance(area, video):
    cv2.namedWindow('video')
    cap = cv2.VideoCapture(video)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    loop_flag = 0
    pos = 0

    cv2.createTrackbar('time', 'video', 0, frames, nothing)
    bs = cv2.createBackgroundSubtractorMOG2()
    es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))

    last_rate = 0

    frames_bar = [0 for x in range(frames)]

    while True:
        if loop_flag == pos:
            loop_flag = loop_flag + 1
            cv2.setTrackbarPos('time', 'video', loop_flag)
        else:
            pos = cv2.getTrackbarPos('time', 'video')
            loop_flag = pos
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos)

        ret, img = cap.read()
        if ret is False:
                break

        if loop_flag % 25 == 0:
            if ret:
                img_area = img[int(area[1]):int(area[1] + area[3]), int(area[0]):int(area[0] + area[2])]
                img_area = cv2.cvtColor(img_area, 6)
                img_area = denoise(img_area, 'Guassian')
                ret, thresh1 = cv2.threshold(img_area.copy(), 127, 255, cv2.THRESH_BINARY)
                fgmask = bs.apply(image=thresh1, learningRate=-1)
                eroded = cv2.erode(fgmask, es)

                SUM = np.sum(eroded / 255)

                rate = SUM
                compare = abs(rate - last_rate)

                if compare < 0:
                    frames_bar[loop_flag] = 1
                elif compare > 20:
                    frames_bar[loop_flag] = 1
            else:
                cap.release()
                break
            last_rate = rate
        elif loop_flag == frames:
            break
        else:
            pass
    return frames_bar


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='arguments of target video')
    parser.add_argument('--in_path', type=str, default='./643-644.mp4')
    parser.add_argument('--area', type=str, default=(251, 87, 98, 152))
    args = parser.parse_args()
    glance(args.area, args.in_path)
