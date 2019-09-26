import glob
import os
import csv
from datetime import datetime, timedelta
from algo2 import Algo as Algo2
from algo3 import Algo as Algo3
from algo6 import Algo as Algo6
from algo7 import Algo as Algo7
from algo4 import Algo as Algo4
from algo5 import Algo as Algo5
from errors import IncomingDataError
from pprint import pprint

MORNING_DATA = "./data/morning/*.csv"
MORNING_DATA_FOLDER = "./data/morning/"
EVENING_DATA_FOLDER = "./data/evening/"
RES_FOLDER = "./data/results/"

DEBUG = False


def one_day(morning_file, evening_file, today_evening_file):
    print(f"Morning file: {morning_file} Evening file: {evening_file}")
    result = {}
    for Algo in [Algo2, Algo3, Algo4, Algo5, Algo6, Algo7]:
        calc = Algo(morning_file, evening_file, today_evening_file, DEBUG)
        calc.calculate()
        # calc.show()
        result[calc.name] = calc.export()
    return result


def swap_nested_dict(src: dict) -> dict:
    res = {}
    for k_outer, v_outer in src.items():
        for k_inner, v_inner in v_outer.items():
            if k_inner not in res:
                res[k_inner] = []
            v_inner["Date"] = k_outer
            res[k_inner].append(v_inner)
    return res


def main():
    result = {}
    for file in glob.glob(MORNING_DATA):
        try:
            today_m, ext = os.path.splitext(os.path.basename(file))
            today = today_m
            today_m = datetime.strptime(today_m, "%d.%m.%Y")
            yesterday_e = today_m - timedelta(days=1)
            yesterday_e = yesterday_e.strftime("%d.%m.%Y")
            yesterday_e = os.path.join(EVENING_DATA_FOLDER, yesterday_e + ext)
            today_e = os.path.join(EVENING_DATA_FOLDER, today + ext)
        except ValueError:
            raise IncomingDataError(f"Некорректное название файла: {file} не может быть датой")

        result[today] = one_day(file, yesterday_e, today_e)

    result = swap_nested_dict(result)
    os.makedirs(RES_FOLDER)
    for algo, result in result.items():
        resf = open(os.path.join(RES_FOLDER, algo + ".csv"), mode="w", encoding="utf-8-sig", newline="\n")
        fp = csv.DictWriter(resf, ["Date", "Buy", "Sell", 'Sum_pos', 'Res', 'Count', 'Cent', 'Mean Price'], dialect="excel-tab", delimiter=";")
        fp.writeheader()
        fp.writerows(result)


if __name__ == "__main__":
    main()
    input("Нажмите кнопку чтобы выйти")
