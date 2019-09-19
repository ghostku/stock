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
    __name__ = 'Y_b /Yra_qery'
    GAP_SELL_PRICE = 250
    GAP_BUY_PRICE = 15

    DELTA_SELL = 0
    DELTA_BUY = 0

    GAP_BUY_X3_1 = -0.5 + DELTA_BUY
    GAP_SELL_X3_1 = 0.1 - DELTA_SELL
    GAP_BUY_X3_2 = -2.5
    GAP_SELL_X3_2 = 2.5

    def __init__(self, morning_data_file, evening_data_file):
        def _rename_columns(prefix, data):
            data.columns = [prefix + name for i, name in enumerate(data.columns)]

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
        self.sell = True

    def _buy_filter(self, row):
        # Volume
        if (row.Volume_m < 500) or (row.Volume_m > 20000):
            return False
        # Price
        if not (self.GAP_BUY_PRICE <= row.Close_m <= self.GAP_SELL_PRICE):
            return False
        # Spread
        if (row.Ask_m - row.Bid_m) * 100 / row.Close_m > 1:
            return False
        # Gap
        if not (self.GAP_BUY_X3_2 <= row.GapBuy <= self.GAP_BUY_X3_1):
            return False
        # Gap Day Before
        if row.Open_e <= 0:
            return False
        if (row.AvgPrice - row.Open_e) * 100 / row.Open_e >= -1.5:
            return False
        return True

    def _sell_filter(self, row):
        # Volume
        if not (2000 < row.Volume_m < 20000):
            return False
        # Price
        if not (self.GAP_BUY_PRICE <= row.Close_m <= self.GAP_SELL_PRICE):
            return False
        # Spread
        if (row.Ask_m - row.Bid_m) * 100 / row.Close_m > 1:
            return False
        # Gap
        if not (self.GAP_SELL_X3_1 <= row.GapSell <= self.GAP_SELL_X3_2):
            return False
        # Gap Day Before
        if row.Open_e <= 0:
            return False
        if -2 < (row.AvgPrice - row.Open_e) * 100 / row.Open_e < 2:
            return False
        return True

    def calculate(self):

        VAL_HZ_5_6 = 0
        VAL_HZ_2_1 = 0
        VAL_HZ_2_4 = 0

        VAL_HZ_1_3 = 1

        self.data["if_1"] = self.data.apply(
            lambda x: x["Last_m"] > 1
            and x["Close_e"] > 0
            and x["Open_e"] > 0
            and x["Open_e"] > 0
            and x["Close_m"] > 0,
            axis=1,
        )
        self.data["AvgPrice"] = (self.data.Bid_m + self.data.Ask_m) / 2
        self.data["GapBuy"] = (
            (self.data.Ask_m - self.data.Close_m) * 100 / self.data.Close_m
        )
        self.data["GapSell"] = (
            (self.data.Bid_m - self.data.Close_m) * 100 / self.data.Close_m
        )

        self.buy = self.data[self.data.apply(self._buy_filter, axis=1)]
        self.sell = self.data[self.data.apply(self._sell_filter, axis=1)]
    
    def show(self):
        print(f'Algo name: {self.__name__}')
        print('\n----- BUY -----\n')
        print(self.buy[['Last_m']])
        print('\n----- SELL ----\n')
        print(self.sell[['Last_m']])