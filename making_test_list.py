#coding=utf-8
import os
import deploy_tool as dt
import funct
import cv2


def get_video_path(dir):
    files = os.listdir(dir)
    current_name = None
    final_list = []
    for i in range(len(files)):
        files[i] = dir + '/' + files[i]
    for file in files:
        in_list = []
        out_list = []
        in_coord = None
        out_coord = None
        station_data = {}
        inside = {}
        outside = {}
        filenames = os.listdir(file)
        for filename in filenames:
            flag = filename[0:2]
            station_name = filename.split('—')[1]
            if not current_name == filename.split('—')[1]:
                out_coord = None
                in_coord = None
            filename = file + '/' + filename
            if flag == '室内' and in_coord is None:
                print(station_name)
                num = input('number of staff?')
                in_coord = dt.get_coord(filename, 'inside', num)
                cv2.destroyAllWindows()
            if flag == '室外' and out_coord is None:
                out_coord = dt.get_coord(filename, 'outside', 1)
                cv2.destroyAllWindows()
            if flag == '室内':
                in_list.append({'path': filename, 'day_flag': funct.get_day_night('室内', filename[-15: -13])})
            if flag == '室外':
                out_list.append({'path': filename, 'day_flag': funct.get_day_night('室外', filename[-15: -13])})
            current_name = station_name
        station_data['Station'] = station_name
        inside['in_coord_list'] = in_coord
        inside['file_list'] = in_list
        outside['out_coord'] = out_coord
        outside['file_list'] = out_list
        station_data['Properties'] = {}
        station_data['Properties']['inside'] = inside
        station_data['Properties']['outside'] = outside
        final_list.append(station_data)
    with open('test_list.txt', 'w') as f:
        f.write(str(final_list))

get_video_path('F:/测试')
