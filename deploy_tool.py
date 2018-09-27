#coding=utf-8
import argparse
import cv2


def get_coord(path, region, region_count):
    region_count = int(region_count)
    if region == 'outside':
        pair_cord_single = []
        pair_cord = ()

        cap = cv2.VideoCapture(path)
        cv2.namedWindow('image')

        point = [0]

        def count(func):
            def call_func(*args):
                func(*args)
                point[0] += 1
            return call_func

        def draw_point(event, x, y, flags, param):
            @count
            def circle(image, pair_cord_single):
                cv2.circle(image, (x, y), 3, (0, 0, 255), -1)
                pair_cord_single.append((x, y))
            if event == cv2.cv2.EVENT_LBUTTONUP:
                circle(image, pair_cord_single)

        cv2.setMouseCallback('image', draw_point)
        ret, image = cap.read()

        for i in range(region_count):
            while 1:
                cv2.imshow('image', image)
                cv2.waitKey(1)
                if point[0] == 4:
                    pair_cord = tuple(pair_cord_single)
                    pair_cord_single = []
                    point[0] = 0
                    break
        return pair_cord
    else:
        cap = cv2.VideoCapture(path)
        ret, frame = cap.read()
        bbox_list = []

        for i in range(region_count):
            bbox = cv2.selectROI(frame, False)
            bbox_list.append(bbox)
    return bbox_list


if __name__ == "__main__":
    # args
    parser = argparse.ArgumentParser(description='arguments of target video')
    parser.add_argument('--path', type=str, default='/User/zjy/video/石门坎站（7.11）0-4点.avi')
    parser.add_argument('--region_count', type=str, default=2)
    args = parser.parse_args()
    
    # get a list of bounding box 
    print(get_coord(args.path, 'inside', 2))


