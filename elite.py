#coding=utf-8
import argparse
import threading
import sleep
import leave
import os


def elite(path, quantity, interval, areas, start_time, save_path):
    threads = []
    for i in range(quantity):
        threads.append(threading.Thread(target=sleep.sleep, args=(path, areas[i], interval, start_time, 'sleep_result' + str(i + 1) + '.txt')))
        if not os.path.exists(save_path + '/' + str(i + 1)):
            os.makedirs(save_path + '/' + str(i + 1))
        else:
            pass
        threads.append(threading.Thread(target=leave.leave, args=(path, areas[i], save_path + '/' + str(i + 1))))
    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == "__main__":
    # args
    parser = argparse.ArgumentParser(description='arguments of target video')
    parser.add_argument('--inside_path', type=str, default='../video/石门坎站（7.11）0-4点.avi')
    parser.add_argument('--quantity', type=int, default=2)
    parser.add_argument('--interval', type=int, default=5 * 60)
    parser.add_argument('--start_time', type=list, default=[2018, 7, 11, 0, 0, 0])
    parser.add_argument('--pic_path', type=str, default='.')
    parser.add_argument('--areas', type=list, default=[(206, 193, 117, 174), (311, 336, 134, 183)])
    args = parser.parse_args()
    elite(args.inside_path, args.quantity, args.interval, args.areas, args.start_time, args.pic_path)
