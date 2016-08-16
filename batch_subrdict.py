import sys
import csv
import os
import re
from collections import deque, OrderedDict



five_min_ms = 300000

interval_regx = re.compile("(\025\d+_\d+\025)")

class FileGroup:
    def __init__(self, lena, cha, silences):
        self.lena_file = lena
        self.cha_file = cha
        self.silence_file = silences

# def collect_files(dir):

def find_all_file_groups(start_dir):
    curr_index = 0
    curr_file = ""

    file_groups = []

    for root, dirs, files in os.walk(start_dir):
        for file in files:
            curr_file = file
            if file_already_in_groups(file, file_groups):
                continue

            if "lena" not in curr_file:
                for file in files:
                    if file[0:5] == curr_file[0:5] and "lena" in file:
                        cha_path = os.path.join(root, curr_file)
                        lena_path = os.path.join(root, file)
                        group = FileGroup(lena_path, cha_path, "randomstuff")
                        file_groups.append(group)
            curr_index += 1

    return file_groups

def file_already_in_groups(file, groups):
    for group in groups:
        if file == os.path.basename(group.lena_file) or \
                        file == os.path.basename(group.cha_file):
            return True
    return False

def read_subr_dict(path):
    subreg_dict = {}

    with open(path, "rU") as input:
        reader = csv.reader(input)
        reader.next()
        prev_file = ""
        for row in reader:
            if row[0] != prev_file:
                subreg_dict[row[0]] = {}

            # make sure it's a legit entry,
            # with all critical values in place
            if row[1] and row[2] and row[3] and row[4]:
                if row[3] == "onset":
                    subreg_dict[row[0]][row[1]] = {}
                    subreg_dict[row[0]][row[1]]["onset"] = row[4]
                    subreg_dict[row[0]][row[1]]["reg_num"] = int(row[1])
                    subreg_dict[row[0]][row[1]]["total_reg_num"] = int(row[2])
                    subreg_dict[row[0]][row[1]]["subr_version"] = "original"
                    subreg_dict[row[0]][row[1]]["old_new"] = "old"

                    if row[5]:
                        subreg_dict[row[0]][row[1]]["rank"] = int(row[5])
                        subreg_dict[row[0]][row[1]]["rank"] = ""
                if row[3] == "offset":
                    if row[1] not in subreg_dict[row[0]]:
                        subreg_dict[row[0]][row[1]] = {}
                        subreg_dict[row[0]][row[1]]["reg_num"] = int(row[1])
                        subreg_dict[row[0]][row[1]]["total_reg_num"] = int(row[2])
                    if row[5]:
                        subreg_dict[row[0]][row[1]]["rank"] = int(row[5])
                    else:
                        subreg_dict[row[0]][row[1]]["rank"] = ""

                    subreg_dict[row[0]][row[1]]["offset"] = row[4]
                    subreg_dict[row[0]][row[1]]["subr_version"] = "original"

            prev_file = row[0]

    return subreg_dict

def filter_file_groups(subr_dict, groups):
    filtered_groups = []
    for index, group in enumerate(groups):
        if os.path.basename(group.cha_file) not in subr_dict:
            filtered_groups.append(group)
    return filtered_groups


def rank_regions(lena_data):
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

def filter_overlaps(ranked_regions, top_n):
    filtered_regions = []

    for region in ranked_regions:
        overlapped = False
        if not filtered_regions:
            filtered_regions.append(region)
            continue
        for index, filtered_region in enumerate(filtered_regions):
            if regions_overlap(region, filtered_region):
                overlapped = True
                break

        if not overlapped:
            filtered_regions.append(region)

        if len(filtered_regions) == top_n:
            return filtered_regions



def regions_overlap(region, filtered_region):
    if region[0] < filtered_region[0] + 12 and \
        region[0] >= filtered_region[0]:
        return True
    if region[0] > filtered_region[0] - 12 and \
        region[0] <= filtered_region[0]:
        return True
    return False


def parse_lena(lena_file):
    lena_data = []
    with open(lena_file, "rU") as input:
        reader = csv.reader(input)
        reader.next()
        for row in reader:
            lena_data.append(row)

    return lena_data


def parse_cha(cha_file, top_n, ranked_regions):
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


def output_new_dictionary(new_regions, original_regions):

    for file in new_regions:
        original_regions.update(file)

    ordered_map = OrderedDict(sorted(original_regions.iteritems()))

    with open(output_file, "wb") as output:
        writer = csv.writer(output)
        writer.writerow(["file", "reg_num", "total_reg_num",
                         "onset", "offset", "rank", "subr_version"])

        for filename, value in ordered_map.iteritems():
            for reg_num, region in value.iteritems():
                writer.writerow([filename, reg_num, region["total_reg_num"],
                                 region["onset"], region["offset"], region["rank"], region["subr_version"]])



def ranked_regions_to_dict(ranked_regions):
    filename = os.path.basename(ranked_regions[0])
    subreg_dict = {filename: {}}

    sorted_regions = sorted(ranked_regions[1], key=lambda region: region[0])

    for index, region in enumerate(ranked_regions[1]):
        region_num = sorted_regions.index(region)+1
        subreg_dict[filename][region_num] = {"reg_num": region_num,
                                             "total_reg_num": len(sorted_regions),
                                             "onset": five_min_ms*region[0],
                                             "offset": five_min_ms*(region[0]+12),
                                             "rank": index+1,
                                             "subr_version": "new"}

    return subreg_dict


if __name__ == "__main__":
    start_dir = sys.argv[1]
    subreg_dict_file = sys.argv[2]
    output_file = sys.argv[3]
    top_n = sys.argv[4]

    subregion_dict = read_subr_dict(subreg_dict_file)
    file_groups = find_all_file_groups(start_dir)

    filtered_groups = filter_file_groups(subregion_dict, file_groups)

    new_regions = []

    lena = None
    for group in filtered_groups:
        lena = parse_lena(group.lena_file)
        ranked_regions = rank_regions(lena)
        filtered_ranked_regions = filter_overlaps(ranked_regions, int(top_n))

        new_file = (group.cha_file, filtered_ranked_regions)
        new_regions.append(new_file)

    new_subregion_dicts = []
    for file in new_regions:
        new_subregion_dicts.append(ranked_regions_to_dict(file))

    output_new_dictionary(new_subregion_dicts, subregion_dict)






