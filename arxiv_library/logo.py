import os
import time

p, _ = os.path.split(__file__)
LOGO_PATH = os.path.join(p, "logo.txt")


def print_logo():
    with open(LOGO_PATH) as logo:
        for line in logo.readlines():
            print(line.replace("\n", ""))
            time.sleep(0.2)
        print("\n")
