#coding=utf-8
import cv2
import numpy as np
import funct


def sleep(path, cord_list, interval, start_time, filename):
    sleep_result = []
    clock = start_time[3]
    day_flag = funct.get_day_night('inside', clock)

    threshold = funct.decide_day(day_flag)

    latest_frm = 0
    cap = cv2.VideoCapture(path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    bs = cv2.createBackgroundSubtractorMOG2(
        varThreshold=threshold)
    es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    frame_cnt = 0
    while True:
        frame_cnt += 1
        stp = funct.format_time(funct.frametotime(fps, start_time, frame_cnt))
        if funct.get_day_night('inside', stp) == day_flag:
            pass
        else:
            th = funct.decide_day(funct.get_day_night('inside', stp))
            day_flag = not day_flag
            bs = cv2.createBackgroundSubtractorMOG2(
                varThreshold=th)
        ret, img = cap.read()
        if ret is False:
            break
        out = img[int(cord_list[1]):int(cord_list[1] + cord_list[3]), int(cord_list[0]):int(cord_list[0] + cord_list[2])]
        grey = cv2.cvtColor(out, 6)
        g_hpf = grey
        g_hpf = funct.denoise(g_hpf, 'median')
        fgmask = bs.apply(g_hpf)
        th = cv2.threshold(fgmask.copy(), 244, 255, cv2.THRESH_BINARY)[1]
        dilated = cv2.dilate(th, es, iterations=2)
        image, contours, hierarchy = cv2.findContours(dilated,
                                                      cv2.RETR_TREE,
                                                      cv2.CHAIN_APPROX_SIMPLE)
        points = []
        for c in contours:
            for point in c:
                points.append(point[0])
            arr_c = np.asarray(points)
            if len(arr_c) > 0:
                if frame_cnt - latest_frm > interval * fps:
                    sleep_result.append((int(latest_frm/fps/60), int(frame_cnt/fps/60)))
                latest_frm = frame_cnt
        cv2.imshow('winname', dilated)
        cv2.waitKey(1)
    with open(filename, 'w') as f:
        f.write(str(sleep_result))



# bbox = (206, 193, 117, 174)
# video = '/Users/zjy/video/石门坎站（7.11）0-4点.avi'
# staaaa = [2018, 7, 2, 16, 0, 12]
# sleep(video, bbox, 300, staaaa, '')
