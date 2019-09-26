from algo import Algo as AlgoBase


class Algo(AlgoBase):
    __name__ = "DEEP # Spy"

    def __init__(self, *args):
        self.GAP_BUY_2 = -0.1
        self.GAP_SELL_2 = 0.1
        self.GAP_BUY_3 = -3.6
        self.GAP_SELL_3 = 3.5

        self.GAP_BUY_PRICE = 15
        self.GAP_SELL_PRICE = 180

        super(Algo, self).__init__(*args)

    def _buy_filter(self, row):
        if not row["if"]:
            return False
        if not (1000 < row.Volume_m):  # Volume
            return False
        if not (self.GAP_BUY_PRICE <= row.Close_m <= self.GAP_SELL_PRICE):  # Price
            return False
        if (row.Ask_m - row.Bid_m) * 100 / row.Close_m > 1:  # Spread
            return False
        if not (self.GAP_BUY_3 <= row.GapBuy <= self.GAP_BUY_2):  # Gap
            return False
        if row.Open_e <= 0:  # Gap Day Before
            return False
        if (row.AvgPrice - row.Open_e) * 100 / row.Open_e >= -4.5:  # Gap Day Before
            return False
        return True

    def _sell_filter(self, row):
        if not row["if"]:
            return False
        if not (2000 < row.Volume_m):  # Volume
            return False
        if not (self.GAP_BUY_PRICE <= row.Close_m <= self.GAP_SELL_PRICE):  # Price
            return False
        if (row.Ask_m - row.Bid_m) * 100 / row.Close_m > 1:  # Spread
            return False
        if not (self.GAP_SELL_2 <= row.GapSell <= self.GAP_SELL_3):  # Gap
            return False
        if row.Open_e <= 0:  # Gap Day Before
            return False
        if -4.5 < (row.AvgPrice - row.Open_e) * 100 / row.Open_e < 2.5:
            return False
        return True

    def calculate(self):
        self.data["if"] = self.data.apply(
            lambda x: x.Last_m > 1 and x.Close_e > 0 and x.Open_e > 0 and x.Close_m > 0, axis=1
        )
        self.data["AvgPrice"] = (self.data.Bid_m + self.data.Ask_m) / 2
        self.data["GapBuy"] = (self.data.Ask_m - self.data.Close_m) * 100 / self.data.Close_m
        self.data["GapSell"] = (self.data.Bid_m - self.data.Close_m) * 100 / self.data.Close_m
        self.data["Result"] = self.data.Close_m * self.data.Last_m / 1000
        self.buy = self.data[self.data.apply(self._buy_filter, axis=1)]
        self.sell = self.data[self.data.apply(self._sell_filter, axis=1)]

