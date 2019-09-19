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
    __name__ = "Y_b /Yra_qery"

    def __init__(self, morning_data_file, evening_data_file):
        self.GAP_SELL_PRICE = 250
        self.GAP_BUY_PRICE = 15

        self.DELTA_SELL = 0
        self.DELTA_BUY = 0

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

    def _buy_filter(self, row):
        if not row["if"]:
            return False
        # Price
        if not (self.GAP_BUY_PRICE <= row.Close_m <= self.GAP_SELL_PRICE):
            return False
        # Spread
        if (row.Ask_m - row.Bid_m) * 100 / row.Close_m > 1:
            return False
        # Gap
        if not (self.GAP_BUY_3 <= row.GapBuy <= self.GAP_BUY_2):
            return False
        # Gap Day Before
        if row.Open_e <= 0:
            return False
        if (row.AvgPrice - row.Open_e) * 100 / row.Open_e >= -1.5:
            return False
        return True

    def _buy_filter_1(self, row):
        if not self._buy_filter(row):
            return False
        # Volume
        if (row.Volume_m < 500) or (row.Volume_m > 20000):
            return False
        return True

    def _buy_filter_2(self, row):
        if not self._buy_filter(row):
            return False
        # Volume
        if row.Volume_m <= 500:
            return False

        return True

    def _sell_filter(self, row):
        if not row["if"]:
            return False
        # Price
        if not (self.GAP_BUY_PRICE <= row.Close_m <= self.GAP_SELL_PRICE):
            return False
        # Spread
        if (row.Ask_m - row.Bid_m) * 100 / row.Close_m > 1:
            return False
        # Gap
        if not (self.GAP_SELL_2 <= row.GapSell <= self.GAP_SELL_3):
            return False
        # Gap Day Before
        if row.Open_e <= 0:
            return False
        return True

    def _sell_filter_1(self, row):
        if not self._sell_filter(row):
            return False
        # Volume
        if not (2000 < row.Volume_m < 20000):
            return False
        # Gap Day Before
        if -2 < (row.AvgPrice - row.Open_e) * 100 / row.Open_e < 2:
            return False
        return True

    def _sell_filter_2(self, row):
        if not self._sell_filter(row):
            return False
        # Volume
        if row.Volume_m <= 2000:
            return False
        # Gap Day Before
        if -1.5 < (row.AvgPrice - row.Open_e) * 100 / row.Open_e < 2:
            return False
        return True

    def calculate(self):
        self.data["if"] = self.data.apply(
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
        self.data["ResultTMP"] = self.data.Close_m * self.data.Last_m / 1000

        count = 0
        while count < 30:
            count += 1
            
            self.GAP_SELL_PRICE = 250
            self.GAP_BUY_2 = -0.5 + self.DELTA_BUY
            self.GAP_SELL_2 = 0.1 - self.DELTA_SELL
            self.GAP_BUY_3 = -2.5
            self.GAP_SELL_3 = 2.5


            self.data["buy_f1"] = self.data.apply(self._buy_filter_1, axis=1)
            self.data["sell_f1"] = self.data.apply(self._sell_filter_1, axis=1)
            GAP_BUY_12 = self.GAP_BUY_2
            GAP_BUY_13 = self.GAP_BUY_3
            GAP_SELL_12 = self.GAP_SELL_2
            GAP_SELL_13 = self.GAP_SELL_3
            
            self.GAP_SELL_PRICE = 180
            self.GAP_BUY_2 = -0.1 + self.DELTA_BUY
            self.GAP_SELL_2 = 0.1 - self.DELTA_SELL
            self.GAP_BUY_3 = -1.5 - (self.DELTA_BUY if self.DELTA_BUY > 0 else 0)
            self.GAP_SELL_3 = 1.5 + (self.DELTA_SELL if self.DELTA_SELL > 0 else 0)

            self.data["buy_f2"] = self.data.apply(self._buy_filter_2, axis=1)
            self.data["sell_f2"] = self.data.apply(self._sell_filter_2, axis=1)

            self.buy = self.data[
                self.data.apply(lambda x: x.buy_f1 or x.buy_f2, axis=1)
            ]
            self.sell = self.data[
                self.data.apply(lambda x: x.sell_f1 or x.sell_f2, axis=1)
            ]
            self.buy["Result"] = self.buy.apply(
                lambda x: x.ResultTMP * (x.buy_f1 + x.buy_f2), axis=1
            )
            self.sell["Result"] = self.sell.apply(
                lambda x: x.ResultTMP * (x.sell_f1 + x.sell_f2), axis=1
            )
            buy_sum = self.buy.sum()
            sell_sum = self.sell.sum()
            tmp_1 = (buy_sum["Result"] - sell_sum["Result"]) / (
                buy_sum["Result"] + sell_sum["Result"]
            )
            buy_qnty = buy_sum['buy_f1'] + buy_sum['buy_f2']
            sell_qnty = sell_sum['sell_f1'] + sell_sum['sell_f2']

            if not count:
                print(f'Iteration: {count}')
                print(f'Buy Sum: {buy_sum["Result"]}')
                print(f'Sell Sum: {sell_sum["Result"]}')
                print(f'TMP_1: {tmp_1}')
                print(f'Buy QNTY: {buy_qnty}')
                print(f'Sell QTY: {sell_qnty}')
                print(f'self.GAP_BUY_PRICE: {self.GAP_BUY_PRICE}')
                print(f'self.GAP_SELL_PRICE: {self.GAP_SELL_PRICE}')

                print(self.buy)
                print(self.sell)
                input('Press any key to continue')
            if tmp_1 > 0.3:
                if buy_qnty > 10:
                    self.DELTA_BUY = self.DELTA_BUY - 0.05
                    self.DELTA_SELL = self.DELTA_SELL + 0.05
                else:
                    self.DELTA_SELL = self.DELTA_SELL + 0.05
            elif tmp_1 < -0.3:
                if sell_qnty > 10:
                    self.DELTA_BUY = self.DELTA_BUY + 0.05
                    self.DELTA_SELL = self.DELTA_SELL - 0.05
                else:
                    self.DELTA_BUY = self.DELTA_BUY + 0.05
            else:
                break

    def show(self):
        print(f"Algo name: {self.__name__}")
        print("\n----- BUY -----\n")
        print(self.buy[["Result"]])
        print("\n----- SELL ----\n")
        print(self.sell[["Result"]])

