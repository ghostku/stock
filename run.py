import glob
import os
from algo2 import Algo as Algo2
from algo3 import Algo as Algo3
from algo6 import Algo as Algo6
from algo7 import Algo as Algo7
from algo4 import Algo as Algo4
from algo5 import Algo as Algo5

MORNING_DATA = "./data/morning/*.csv"
EVENING_DATA_FOLDER = "./data/evening/"

DEBUG = False


def one_day(morning_file, evening_file):
    print(f"Morning file: {morning_file}")
    print(f"Evening file: {evening_file}")
    for Algo in [Algo2, Algo3, Algo4, Algo5, Algo6, Algo7]:
        calc = Algo(morning_file, evening_file, DEBUG)
        calc.calculate()
        calc.show()


def main():
    # 1 Загрузить данные
    for file in glob.glob(MORNING_DATA):
        one_day(file, os.path.join(EVENING_DATA_FOLDER, os.path.basename(file)))


if __name__ == "__main__":
    main()
    input("Нажмите кнопку чтобы выйти")
