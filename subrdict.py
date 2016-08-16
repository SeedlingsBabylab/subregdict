import csv
import sys
import os
import re

from collections import deque

lena_data = []

five_min_ms = 300000

interval_regx = re.compile("(\025\d+_\d+\025)")

def parse_lena(lena_file):
    with open(lena_file, "rU") as input:
        reader = csv.reader(input)
        reader.next()
        for row in reader:
            lena_data.append(row)

def rank_regions():
    start = 0
    end = 12

    region_values = []
    window = lena_data[start:end]

    region_count = 0
    while end <= len(lena_data):
        ctc_cvc_avg_sum = 0
        for entry in window:
            ctc_cvc_avg = (float(entry[21]) + float(entry[24])) / 2.0
            ctc_cvc_avg_sum += ctc_cvc_avg
        region_values.append((region_count, ctc_cvc_avg_sum))

        start += 1
        end += 1
        region_count += 1
        window = lena_data[start:end]

    ranked_regions = sorted(region_values,
                            key=lambda region: region[1],
                            reverse=True)
    return ranked_regions

def output_ranked_lena(top_n, ranked_regions):
    file_base = os.path.basename(lena_file)
    filename = lena_file.replace(".csv", "_ranked_regions.csv")
    with open(filename, "wb") as output:
        writer = csv.writer(output)
        writer.writerow(["filename", "region_rank", "onset", "offset"])
        for index, element in enumerate(ranked_regions[:top_n]):
            writer.writerow([file_base, str(index+1), str(element[0]*five_min_ms), str((element[0]+12)*five_min_ms)])
    print ranked_regions[:top_n]

def parse_cha(top_n, ranked_regions):
    region_queue = deque(rank_regions[:top_n])

    curr_region = region_queue.popleft()

    with open(cha_file, "rU") as input_cha:
        for line in input_cha:
            regx_result = interval_regx.search(line)
            if regx_result:
                interval = regx_result.group(1)
                split_interval = interval.replace("\x15", "", 2).split("_")
                split_interval = map(int, split_interval)

                print split_interval





if __name__ == "__main__":
    cha_file = sys.argv[1]
    lena_file = sys.argv[2]
    silence_file = sys.argv[3]

    parse_lena(lena_file)
    ranked_regions = rank_regions()
    parse_cha(5, rank_regions)

    output_ranked_lena(5, ranked_regions)
