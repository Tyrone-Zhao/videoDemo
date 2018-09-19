import tensorflow as tf
import cv2
import numpy as np
from tools import denoise
from tools import nothing
import argparse


def sleep(area, video):
    cv2.namedWindow('video')
    cap = cv2.VideoCapture(video)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    loop_flag = 0
    pos = 0

    cv2.createTrackbar('time', 'video', 0, frames, nothing)
    bs = cv2.createBackgroundSubtractorMOG2()
    es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))

    # fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # out = cv2.VideoWriter('./test/output.avi', fourcc, 25.0, size)
    # last_rate = 0
    current = 0

    frames_bar = [0 for x in range(frames)]

    with tf.Session() as sess:
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

            img_area = img[int(area[1]):int(area[1] + area[3]), int(area[0]):int(area[0] + area[2])]
            if loop_flag == 1:
                compare = img_area
            grey = cv2.cvtColor(img_area, 6)

            g_hpf = denoise(grey, 'Guassian')
            fgmask = bs.apply(g_hpf)
            th = cv2.threshold(fgmask.copy(), 244, 255, cv2.THRESH_BINARY)[1]
            dilated = cv2.dilate(th, es, iterations=2)
            image, contours, hierarchy = cv2.findContours(dilated,
                                                          cv2.RETR_TREE,
                                                          cv2.CHAIN_APPROX_SIMPLE)
            points = []
            sum = 0
            for c in contours:
                for point in c:
                    points.append(point[0])
                arr_c = np.asarray(points)
                sum += len(arr_c)
            if sum < 10 and loop_flag - current > 125:
                compare = tf.image.convert_image_dtype(compare, tf.float32)
                tmp = tf.image.convert_image_dtype(img_area, tf.float32)
                value = tf.image.ssim(compare, tmp, max_val=255)
                simi = sess.run(value)
                if 1 - simi > 0.003:
                    frames_bar[loop_flag] = 1
                current = loop_flag
            else:
                pass
    return frames_bar


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='arguments of target video')
    parser.add_argument('--in_path', type=str, default='./643-644.mp4')
    parser.add_argument('--area', type=str, default=(251, 87, 98, 152))
    args = parser.parse_args()
    sleep(args.area, args.in_path)

