from algo import Algo as AlgoBase


class Algo(AlgoBase):
    __name__ = "B_o /BALANCE OLD/PreMarket_b_old/balans_standart"
    AUTO_POSITION = 1

    def __init__(self, *args):
        self.GAP_SELL_PRICE = 250
        self.GAP_BUY_PRICE = 15

        self.GAP_BUY_2 = -0.2
        self.GAP_SELL_2 = 0.2
        self.GAP_BUY_3 = -3.5
        self.GAP_SELL_3 = 3.5

        super(Algo, self).__init__(*args)

    def _buy_filter(self, row):
        if not row["if"]:
            return False
        if not (1000 < row.Volume_m < 20000):  # Volume
            return False
        if not (self.GAP_BUY_PRICE <= row.Close_m <= self.GAP_SELL_PRICE):  # Price
            return False
        if (row.Ask_m - row.Bid_m) * 100 / row.Close_m > 1:  # Spread
            return False
        if not (self.GAP_BUY_3 <= row.GapBuy <= self.GAP_BUY_2):  # Gap
            return False
        if row.Open_e <= 0:  # Gap Day Before
            return False
        if (row.AvgPrice - row.Open_e) * 100 / row.Open_e >= -1.5:  # Gap Day Before
            return False
        return True

    def _buy_filter_1(self, row):
        if not self._buy_filter(row):
            return False
        return True

    def _buy_filter_2(self, row):
        if not self._buy_filter(row):
            return False
        return True

    def _sell_filter(self, row):
        if not row["if"]:
            return False
        if not (2000 < row.Volume_m < 20000):  # Volume
            return False
        if not (self.GAP_BUY_PRICE <= row.Close_m <= self.GAP_SELL_PRICE):  # Price
            return False
        if (row.Ask_m - row.Bid_m) * 100 / row.Close_m > 1:  # Spread
            return False
        if not (self.GAP_SELL_2 <= row.GapSell <= self.GAP_SELL_3):  # Gap
            return False
        if row.Open_e <= 0:  # Gap Day Before
            return False
        if -1.5 < (row.AvgPrice - row.Open_e) * 100 / row.Open_e < 2:
            return False
        return True

    def _sell_filter_1(self, row):
        if not self._sell_filter(row):
            return False
        return True

    def _sell_filter_2(self, row):
        if not self._sell_filter(row):
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
        for count in range(1, 27):
            CELL_5_6 = 0

            self.data["buy_f1"] = self.data.apply(self._buy_filter_1, axis=1)
            self.data["sell_f1"] = self.data.apply(self._sell_filter_1, axis=1)

            self.buy = self.data[self.data.apply(lambda x: x.buy_f1, axis=1)]
            self.sell = self.data[self.data.apply(lambda x: x.sell_f1, axis=1)]

            if self.AUTO_POSITION == 1:
                AUTO_GAP_BUY_12 = self.GAP_BUY_2
                AUTO_GAP_BUY_13 = self.GAP_BUY_3
                AUTO_GAP_SELL_12 = self.GAP_SELL_2
                AUTO_GAP_SELL_13 = self.GAP_SELL_3

                buy_sum = self.buy.sum()
                sell_sum = self.sell.sum()
                tmp_1 = (buy_sum["Result"] - sell_sum["Result"]) / (buy_sum["Result"] + sell_sum["Result"])
                buy_qnty = buy_sum["buy_f1"]  # + buy_sum["buy_f2"]
                sell_qnty = sell_sum["sell_f1"]  # + sell_sum["sell_f2"]
                total_qnty = buy_qnty + sell_qnty

                if (tmp_1 > 0.2) and (self.GAP_BUY_2 > -1):
                    self.GAP_BUY_2 -= 0.05
                    self.GAP_SELL_2 -= 0.05
                    if total_qnty <= 4:
                        self.GAP_SELL_3 += 0.05
                elif (tmp_1 < -0.2) and (self.GAP_SELL_2 > -1):
                    self.GAP_BUY_2 += 0.05
                    self.GAP_SELL_2 += 0.05
                    if total_qnty <= 4:
                        self.GAP_BUY_3 -= 0.05
                else:
                    break

        # Второй этап
        self.GAP_BUY_2 = -0.2
        self.GAP_SELL_2 = 0.2
        self.GAP_BUY_3 = -3.5
        self.GAP_SELL_3 = 3.5

        self.data["buy_f2"] = self.data.apply(self._buy_filter_2, axis=1)
        self.data["sell_f2"] = self.data.apply(self._sell_filter_2, axis=1)

        self.buy = self.data[self.data.apply(lambda x: x.buy_f2, axis=1)]
        self.sell = self.data[self.data.apply(lambda x: x.sell_f2, axis=1)]
