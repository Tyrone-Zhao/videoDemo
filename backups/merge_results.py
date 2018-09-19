import funct
import argparse

# args
parser = argparse.ArgumentParser(description='arguments of target video')
parser.add_argument('--i', type=int, default=0)
args = parser.parse_args()


def get_elite_results(i):
    result_file_name = funct.get_file_name("final_sleep_result", i)
    result_path = funct.get_coord_path(result_file_name)
    result_f = open(result_path, "w")
    leave_file_name = funct.get_file_name("leave_result", i)
    leave_path = funct.get_coord_path(leave_file_name)
    leave_f = open(leave_path, "rt").readlines()
    sleep_file_name = funct.get_file_name("sleep_result", i)
    sleep_path = funct.get_coord_path(sleep_file_name)
    sleep_f = open(sleep_path, "rt").readlines()
    for sleep_ts in sleep_f:
        overlap_flag = False
        for leave_ts in leave_f:
            sleep_ts_spt = sleep_ts.split("-")
            leave_ts_spt = leave_ts.split("-")
            leave_interval = [int(leave_ts_spt[0]), int(leave_ts_spt[1])]
            sleep_interval = [int(sleep_ts_spt[0]), int(sleep_ts_spt[1])]
            overlap = funct.get_overlap(leave_interval, sleep_interval)
            if overlap > 0:
                overlap_flag = True
        if overlap_flag == False:
            print(sleep_ts.strip(), file=result_f)


if __name__ == "__main__":
    get_elite_results(args.i)

