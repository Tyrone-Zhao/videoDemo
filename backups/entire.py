import cv2
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import funct
import argparse
import numpy as np
import threading
import time


def leave(in_path, out_path, cord_list, interval, out_list, inside_day_flag):
    ori_coin = 1
    differ = 0
    cap = cv2.VideoCapture(in_path)
    ret, frame = cap.read()
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(fps, 'in')

    # bbox = cv2.selectROI(frame, False)
    bbox = cord_list
    orig_bbox = bbox
    tracker = cv2.TrackerKCF_create()
    ret = tracker.init(frame, bbox)
    num = 0
    mog = cv2.createBackgroundSubtractorMOG2()
    leave_flag = False  # 人是否在岗，真为不在
    leave_stp = 0
    come_stamp = -1
    outside_nobody = -1
    true_count = 0

    while True:
        num = num + 1
        ret, frame = cap.read()
        if not ret:
            break
        img = frame
        if leave_flag is False:
            ok, bbox = tracker.update(frame)
            if ok:
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
            else:
                cv2.putText(frame, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255),
                            2)
            cv2.putText(frame, " KCF Tracker", (100, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2)
            cv2.rectangle(frame, (int(orig_bbox[0]), int(orig_bbox[1])),
                          (int(orig_bbox[0] + orig_bbox[2]), int(orig_bbox[1] + orig_bbox[3])), (255, 255, 0), 2, 1)
            cv2.imshow("Tracking", frame)
            cv2.waitKey(1)
            coincide = funct.solve_coincide(
                (int(orig_bbox[0]), int(orig_bbox[1]), int(orig_bbox[0] + orig_bbox[2]),
                 int(orig_bbox[1] + orig_bbox[3])),
                (int(bbox[0]), int(bbox[1]), int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3])))
            if num % 25 == 0:
                if coincide is not False:
                    differ = abs(coincide - ori_coin)
                    ori_coin = coincide
                    if differ > 0.3:
                        leave_flag = True
                        print('inside has left')
                        leave_stp = time.time()
                        leave_pic = num
                        come_stamp = -1
                        oflag, ots = outside_leave(out_path, num, out_list, inside_day_flag, interval-25*60)
                        if oflag is True:
                            cap.set(cv2.CAP_PROP_POS_FRAMES, ots)
                            num = ots
                            outside_nobody = True
                            pass
                        else:
                            cap.set(cv2.CAP_PROP_POS_FRAMES, ots)
                            outside_nobody = False
                            num = ots
                            leave_stp = time.time()
        else:
            if funct.if_people(img, mog, funct.small(orig_bbox)) and time.time() - leave_stp > 30 and come_stamp is -1:
                true_count += 1
                if true_count >= 75:
                    tracker = cv2.TrackerKCF_create()
                    ret = tracker.init(frame, orig_bbox)
                    come_stamp = time.time()
                    if outside_nobody:
                        print('come', num)
                        outside_nobody = -1
                    elif outside_nobody is False:
                        print(leave_stp, 'liangshijian')
                        outside_nobody = -1
                    else:
                        pass
                    come_pic = num
                    if come_pic - leave_pic > interval:
                        print('leave', leave_pic, come_pic)
                else:
                    pass
            else:
                pass
            if come_stamp is not -1 and time.time() - come_stamp > 30:
                ori_coin = 1
                come_stamp = -1
                leave_flag = False


def outside_leave(path, start_frm, coordinate, inside_day_flag, interval):
    def night_enter(path, start_frm, coordinate):
        cap = cv2.VideoCapture(path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frm)
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(fps)
        mog = cv2.createBackgroundSubtractorMOG2()
        loop_flag = start_frm
        false_cnt = 0
        true_cnt = 0
        enter = -1
        leave = -1
        while True:
            loop_flag = loop_flag + 1
            ret, img = cap.read()
            if ret == False:
                break
            show_img = img
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

            cv2.drawContours(show_img, contours, -1, (0, 0, 0), 3)
            cv2.imshow('outside', show_img)
            cv2.waitKey(1)
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
                    if leave - enter >= interval:
                        return True, leave
                    else:
                        return False, leave
                else:
                    pass
            else:
                pass
            if loop_flag - start_frm < interval:
                pass
            else:
                print('leave happen')
                return True, loop_flag

    def day_enter(path, start_frm, coordinate):
        cap = cv2.VideoCapture(path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frm)
        bs = cv2.createBackgroundSubtractorMOG2(varThreshold=500)
        es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        frame_cnt = start_frm
        leave_list = []
        while True:
            frame_cnt += 1
            ret, img = cap.read()
            reach = -1
            leave = -1
            if ret == False:
                break
            g_hpf = img
            g_hpf = funct.denoise(g_hpf, "median")
            fgmask = bs.apply(g_hpf)
            th = cv2.threshold(fgmask.copy(), 244, 255, cv2.THRESH_BINARY)[1]
            dilated = cv2.dilate(th, es, iterations=2)
            image, contours, hierarchy = cv2.findContours(dilated,
                                                      cv2.RETR_TREE,
                                                      cv2.CHAIN_APPROX_SIMPLE)
            if frame_cnt % 100 == 1:
                coord_list = []
            for c in contours:
                extBot = tuple(c[c[:, :, 1].argmax()][0])
                if cv2.contourArea(c) > 1600:
                    cv2.drawContours(img, [c], -1, (0, 255, 0), 2)
                    coord_list.append(extBot)
                    M = cv2.moments(c)
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    polygon = Polygon(coordinate)
                    point = Point((cX, cY))
                    contain_flag = polygon.contains(point)
                    if contain_flag == True and len(coord_list) > 1:
                        result = funct.intersection(coord_list[-2][0],
                                            coord_list[-2][1],
                                            coord_list[-1][0],
                                            coord_list[-1][1],
                                            coordinate[2][0],
                                            coordinate[2][1],
                                            coordinate[3][0],
                                            coordinate[3][1])
                        if result == True:
                            leave_list.append(frame_cnt)
                            if len(leave_list) == 2:
                                 reach = leave_list[0]
                                 leave = leave_list[1]
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
                if frame_cnt - start_frm < interval:
                    pass
                else:
                    if reach == -1:
                        return True, frame_cnt
                    else:
                        return False, frame_cnt

    if inside_day_flag == 1:
        return day_enter(path, start_frm, coordinate)
    else:
        return night_enter(path, start_frm, coordinate)


def sleep(path, i, cord_list, interval, inside_day_flag):
    if inside_day_flag == 0:
        threshold = 1000
    else:
        threshold = 800
    sleep_file_name = funct.get_file_name("sleep_result", i)
    sleep_result_path = funct.get_coord_path(sleep_file_name)

    with open(sleep_result_path, "w") as result_f:
        latest_frm = 0
        cap = cv2.VideoCapture(path)
        bs = cv2.createBackgroundSubtractorMOG2(
            varThreshold=threshold)
        es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        frame_cnt = 0
        while True:
            frame_cnt += 1
            ret, img = cap.read()
            if ret is False:
                break
            out = img[int(cord_list[1]):int(cord_list[1] + cord_list[3]),
                  int(cord_list[0]):int(cord_list[0] + cord_list[2])]
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
                    (x, y, w, h) = cv2.boundingRect(c)
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0),
                                  2)
                    if frame_cnt - latest_frm > interval:
                        print(str(latest_frm) + "-" + str(frame_cnt),
                              file=result_f)
                    latest_frm = frame_cnt


def main(in_path, out_path, cord_list, interval, out_list, inside_day_flag, quantity):
    Threads = []
    for i in range(0, quantity):
        Threads.append(threading.Thread(target=leave, args=(in_path, out_path, cord_list, interval, out_list, inside_day_flag)))
        Threads.append(threading.Thread(target=sleep, args=(in_path, i, cord_list, interval, inside_day_flag)))
    for t in Threads:
        t.start()
    for t in Threads:
        t.join()


if __name__ == "__main__":
    # args
    parser = argparse.ArgumentParser(description='arguments of target video')
    parser.add_argument('--inside_path', type=str, default='./室内—渡市站—0：05—4：05.avi')
    parser.add_argument('--outside_path', type=str, default='./室外—渡市站—0：05—4：05.avi')
    parser.add_argument('--quantity', type=int, default=1)
    parser.add_argument('--interval', type=int, default=25 * 5 * 60)
    parser.add_argument('--day_flag', type=int, default=0)
    args = parser.parse_args()
    inside_cord_arry = (245, 291, 275, 246)
    outside_cord_arry = [[(378, 348), (384, 492), (453, 472), (442, 331)]]
    main(args.inside_path, args.outside_path, inside_cord_arry, args.interval, outside_cord_arry, args.day_flag, args.quantity)
    # args.day_flag = get_day_night('室内', start_ts)


