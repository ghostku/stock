import pandas as pd
import numpy as np

CSV_DTYPES = {"Last": np.single, "Close": np.single}
CSV_NA_VALUES = {
    "Last": ["<empty>"],
    "Close": ["<empty>"],
    "Open": ["<empty>"],
    "Bid": ["<empty>"],
    "Ask": ["<empty>"],
    "Volume": ["<empty>", ""],
}


class Algo:
    def __init__(self, morning_data_file, evening_data_file, debug=False):
        self.debug = debug
        self.morning = pd.read_csv(
            morning_data_file,
            index_col="Symbol",
            na_values=CSV_NA_VALUES,
            skiprows=3,
            thousands=",",
        )
        self.evening = pd.read_csv(
            evening_data_file,
            index_col="Symbol",
            na_values=CSV_NA_VALUES,
            skiprows=3,
            thousands=",",
        )
        self.data = self.morning.join(self.evening, lsuffix="_m", rsuffix="_e")
        self.buy = None
        self.sell = None

    def calculate(self):
        pass

    def show(self):
        print(f"Algo name: {self.__name__}")
        print("\n----- BUY -----\n")
        try:
            print(self.buy[["Result"]])
        except TypeError:
            pass
        print("\n----- SELL ----\n")
        try:
            print(self.sell[["Result"]])
        except TypeError:
            pass
