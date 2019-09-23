import glob
import os
from algo3 import Algo as Algo3
from algo4 import Algo as Algo4


MORNING_DATA = "./data/morning/*.csv"
EVENING_DATA_FOLDER = "./data/evening/"


def one_day(morning_file, evening_file):
    print(f"Morning file: {morning_file}")
    print(f"Evening file: {evening_file}")
    calc1 = Algo3(morning_file, evening_file, True)
    calc1.calculate()
    calc1.show()
    calc4 = Algo4(morning_file, evening_file, True)
    calc4.calculate()
    calc4.show()

def main():
    # 1 Загрузить данные
    for file in glob.glob(MORNING_DATA):
        one_day(file, os.path.join(EVENING_DATA_FOLDER, os.path.basename(file)))


if __name__ == "__main__":
    main()
    input("Нажмите кнопку чтобы выйти")
