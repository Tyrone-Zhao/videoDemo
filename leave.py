#coding=utf-8
import cv2
import funct
import numpy as np


def go_away(cap, work_area, mog, tracker, frame, save_path):
    lastframe_coin = 1  # 初始相交面积
    s_coin = 1
    pun_list = []  # 辅助判定列表
    switch = True  # 允许自动重置
    switch_timer = 0  # 重置的计时器
    fps = int(cap.get(cv2.CAP_PROP_FPS))  # 视频帧率
    cir_num = 0
    one_min = 0
    while True:
        cir_num = cir_num + 1
        switch_timer += 1
        frame = frame + 1
        ret, img = cap.read()
        pure_img = img
        tracker.init(img, work_area)  # 初始化追踪器
        ok, box = tracker.update(img)
        if switch_timer % (180 * fps) == 0 and switch:  # 自动重置追踪的计时器，防飘，三分钟一次
            tracker = cv2.TrackerKCF_create()

        if ok:
            # 计算两框相交面积
            coincide = funct.solve_coincide(
                (int(box[0]), int(box[1]), int(box[0] + box[2]),
                 int(box[1] + box[3])),
                (int(work_area[0]), int(work_area[1]), int(work_area[0] + work_area[2]), int(work_area[1] + work_area[3])))

            # 如果连续1分钟候选框没有移动，认为人已离岗，补充kcf的缺漏（supplement）
            s_differ = abs(coincide - s_coin)
            if s_differ == 0:
                one_min += 1
                if one_min >= fps * 60:
                    cv2.imwrite(save_path + '/' + str(frame) + '.jpg', img)
                    return frame
            else:
                one_min = 0
            s_coin = coincide

            if frame % fps == 0:  # 每隔一秒
                if coincide is not False:
                    differ = abs(coincide - lastframe_coin)
                    lastframe_coin = coincide
                    if differ > 0.3 or coincide < 0.5:  # 相交面积小于50% 或 相交面积变化大于30%
                        people = funct.if_people(pure_img, mog, work_area)  # 看有没有动静
                        switch_timer = 1
                        switch = False  # 关闭重置
                        pun_list.append(people)  # 在岗情况压栈
                        if len(pun_list) >= 10:  # 10秒进行一次判断
                            if np.sum(pun_list) >= 5:  # 阈值大于5 认为有人
                                switch = True  # 打开开关,开始定时重置
                                pun_list = []
                                tracker = cv2.TrackerKCF_create()
                            else:
                                return frame
                        else:
                            pass
                    else:
                        switch = True
                        pun_list = []
                else:
                    pass
            else:
                pass
        else:
            if cir_num > (fps * 20):
                cv2.imwrite(save_path + '/' + str(frame) + '.jpg', img)
                return frame
            else:
                tracker = 1
                tracker = cv2.TrackerKCF_create()


def come_back(frame, box_mid, p1, p2, cap, height, width, mog, work_area, save_path):
    _, now = cap.read()
    now = cv2.cvtColor(now, cv2.COLOR_BGR2GRAY)
    now = funct.denoise(now, 'median')
    fps = cap.get(cv2.CAP_PROP_FPS)

    v = []

    while True:
        ret, img = cap.read()
        frame += 1

        img_diff = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_diff = funct.denoise(img_diff, 'median')

        mask = np.zeros((int(height), int(width)))
        cv2.rectangle(mask, p1, p2, 1, -1, 1)
        mask = mask.astype(np.bool)
        g_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        g_img = g_img * mask
        g_img = funct.denoise(g_img, 'median')
        fgmask = mog.apply(g_img)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        fgmask = cv2.erode(fgmask, kernel, iterations=1)
        fgmask = cv2.dilate(fgmask, kernel)

        _, contours, hierarchy1 = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        points = []
        min_x = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        min_y = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        max_x = 0
        max_y = 0

        rect_point = []
        for c in contours:
            if cv2.contourArea(c) > 1600:
                x, y, w, h = cv2.boundingRect(c)
                rect_point.append((x, y))
                rect_point.append((x + w, y + h))
                for point in c:
                    points.append(point[0])
            else:
                pass
        for point in rect_point:
            x = int(point[0])
            y = int(point[1])
            if x < min_x:
                min_x = x
            if y < min_y:
                min_y = y
            if x > max_x:
                max_x = x
            if y > max_y:
                max_y = y

        boxes = (min_x, min_y, max_x - min_x, max_y - min_y)

        points = np.asarray(points)
        x, y = funct.poly_center(points)

        if len(v) < 2:
            if frame % fps == 0:
                if (x, y) == (-1, -1):
                    pass
                else:
                    v.append((int(x), int(y)))
        else:
            if frame % fps == 0:
                if (x, y) == (-1, -1):
                    pass
                else:
                    v.append((int(x), int(y)))
                    v.remove(v[0])
                    for i in range(len(v) - 1):
                        v_x = v[i + 1][0] - v[i][0]
                        v_y = v[i + 1][1] - v[i][1]
                        vector = (v_x, v_y)
                        if not vector == (0, 0):
                            horizion, vertical = funct.signal(v[i][0], v[i][1], box_mid[0], box_mid[1])
                            v_horizion, v_vertical = funct.signal(vector[0], vector[1], 0, 0)
                            if (horizion ^ v_horizion, vertical ^ v_vertical) == (True, True):
                                show_img = img_diff - now
                                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
                                show_img = cv2.erode(show_img, kernel, iterations=1)
                                _, contours, hierarchy1 = cv2.findContours(show_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                                total_area = boxes[2] * boxes[3]
                                if total_area > (work_area[2] * work_area[3] / 4):
                                    cv2.imwrite(save_path + '/' + str(frame) + '.jpg', img)
                                    return frame
        now = img_diff


def leave(file, work_area, save_path):
    tracker = cv2.TrackerKCF_create()
    mog = cv2.createBackgroundSubtractorMOG2()
    # work_area = (314, 318, 144, 169) #1
    # video = './关在站（7.2）20-0点.avi' #2
    video = file
    cap = cv2.VideoCapture(video)
    total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    work_mid = (int(work_area[0] + 0.5 * work_area[2]), int(work_area[1] + 0.5 * work_area[3]))
    LU_pt = (int(work_area[0]), int(work_area[1]))
    RD_pt = (int(work_area[0] + work_area[2]), int(work_area[1] + work_area[3]))
    frame = 0
    try:
        while True:
            frame = go_away(cap, work_area, mog, tracker, frame, save_path)
            # print('leave at' + str(frame))
            frame = come_back(frame, work_mid, LU_pt, RD_pt, cap, height, width, mog, work_area, save_path)
            # print('come at' + str(frame))
    except Exception as e:
        print('finish')