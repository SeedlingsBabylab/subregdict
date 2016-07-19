import sys
import subprocess as sp

class FileGroup:
    def __init__(self, lena, cha, silences):
        self.lena_file = lena
        self.cha_file = cha
        self.silence_file = silences

def collect_files(dir):



if __name__ == "__main__":
    start_dir = sys.argv[1]

    file_groups = collect_files(start_dir)

    for group in file_groups:
        command = ["python", "subregdict.py", group.cha_file, group.lena_file, group.silence_file]

        command_string = " ".join(command)
        print command_string

        pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10 ** 8)
        out, err = pipe.communicate()
