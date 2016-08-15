import sys
import subprocess as sp

class FileGroup:
    def __init__(self, lena, cha, silences):
        self.lena_file = lena
        self.cha_file = cha
        self.silence_file = silences

# def collect_files(dir):

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
                        subreg_dict[row[0]][row[1]]["reg_num"] = row[1]
                        subreg_dict[row[0]][row[1]]["total_reg_num"] = row[2]
                        if row[5]:
                            subreg_dict[row[0]][row[1]]["rank"] = row[5]
                    if row[3] == "offset":
                        subreg_dict[row[0]][row[1]]["offset"] = row[4]

            prev_file = row[0]



if __name__ == "__main__":
    start_dir = sys.argv[1]
    subreg_dict_file = sys.argv[2]

    subregion_dict = read_subr_dict(subreg_dict_file)

    print "hello"

    # file_groups = collect_files(start_dir)
    #
    # for group in file_groups:
    #     command = ["python", "subregdict.py", group.cha_file, group.lena_file, group.silence_file]
    #
    #     command_string = " ".join(command)
    #     print command_string
    #
    #     pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10 ** 8)
    #     out, err = pipe.communicate()
