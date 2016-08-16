import csv
import sys
import re

reg_num_regx = re.compile("(\d+) of (\d+)")
rank_regx = re.compile("ranked (\d+) of (\d+)")

def parse_comments(comments):
    results = []
    for row in comments:
        temp = [None]*6
        temp[0] = row[0]

        regx_result = reg_num_regx.search(row[3])

        if regx_result:
            temp[1] = regx_result.group(1)
            temp[2] = regx_result.group(2)

        if "starts" in row[3]:
            temp[3] = "onset"
        elif "ends" in row[3]:
            temp[3] = "offset"
        else:
            continue

        temp[4] = row[2]

        rank_regx_result = rank_regx.search(row[3])
        if rank_regx_result:
            temp[5] = rank_regx_result.group(1)

        results.append(temp)
    return results

if __name__ == "__main__":
    comments_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(comments_file, "rU") as input:
        reader = csv.reader(input)
        header = reader.next()
        parsed_subregions = parse_comments(reader)

        with open(output_file, "wb") as output:
            writer = csv.writer(output)
            writer.writerow(["file", "region_num", "total_reg_num", "on_or_off", "timestamp", "rank"])
            writer.writerows(parsed_subregions)
