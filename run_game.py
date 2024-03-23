from main import start_game 
import sys

if __name__ == "__main__":

    TESTED_VERSION = (3, 10)
    MIN_VERSION = (3,0)

    if sys.version_info[:2] < TESTED_VERSION:
        print("This game was developed using python 3.10. There may be compablity issues with other python versions")
    elif sys.version_info[:2] < MIN_VERSION: 
        sys.exit("This game requires Python3")

    start_game()
