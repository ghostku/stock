import pandas as pd
import numpy as np

pd.options.mode.chained_assignment = None  # default='warn'

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
    def __init__(self, morning_data_file, evening_data_file, today_evening_data_file, debug=False):
        self.debug = debug
        self.morning = pd.read_csv(
            morning_data_file, index_col="Symbol", na_values=CSV_NA_VALUES, skiprows=3, thousands=","
        )
        self.evening = pd.read_csv(
            evening_data_file, index_col="Symbol", na_values=CSV_NA_VALUES, skiprows=3, thousands=","
        )
        self.today_evening = pd.read_csv(
            today_evening_data_file, index_col="Symbol", na_values=CSV_NA_VALUES, skiprows=3, thousands=","
        )
        self.data = self.morning.join(self.evening, lsuffix="_m", rsuffix="_e")
        self.buy = None
        self.sell = None

    @property
    def name(self):
        return self.__name__

    def calculate(self):
        pass

    def show(self):
        print(f"Algo name: {self.__name__}")
        print("\n----- BUY -----\n")
        if len(self.buy.index):
            print(self.buy[["Result"]])
        print("\n----- SELL ----\n")
        if len(self.sell.index):
            print(self.sell[["Result"]])
        
    def export(self):
        total_index = list(self.buy.index) + list(self.sell.index)
        df = self.today_evening[self.today_evening.index.isin(total_index)]
        df['Res'] = df.Last - df.Open
        try:
            df['Res'] = df.apply(lambda x: x.Res * (-1 if x.name in list(self.sell.index) else 1), axis=1)
        except ValueError:
            pass
        Sum_pos = df.sum()['Open']
        Res =  df.sum()['Res']
        Count = len(self.buy.index) + len(self.sell.index)
        result = {
            'Buy': list(self.buy.index),
            'Sell': list(self.sell.index),
            'Count': Count,
            'Sum_pos': Sum_pos,
            'Res': Res,
            'Cent': Res / Sum_pos,
            'Mean Price': Sum_pos / Count
        }
        return result
