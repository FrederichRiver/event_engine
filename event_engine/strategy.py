#!/usr/bin/python3
from unicodedata import name
from libsql_utils.transaction import get_n_day_before_date
from libsql_utils.engine import engine_init
from pandas import DataFrame
import matplotlib.pyplot as plt
from libsql_utils.model.trade import formOrderSet
from sqlalchemy.orm import Session


class StrategyBase(object):
    def __init__(self, df: DataFrame) -> None:
        for n in [5, 10, 20]:
            df[f"MA{n}"] = df['close'].rolling(n).mean()
        self.df = df.dropna(axis=0)
        self.index = (i for i in self.df.index)

    def step(self, index):
        row = self.df.loc[index]
        if (row['MA5'] < row['MA10']) and (abs(row['close'] - row['MA5'])/row['close'] < 0.01):
            flag = True
        else:
            flag = False
        return flag

    def plot(self):
        plt.figure(figsize=(12, 4), dpi=72)
        plt.ylim(22, 27)
        plt.plot(self.df.index, self.df['close'], label="close")
        plt.plot(self.df.index, self.df['MA5'], label="ma5")
        plt.plot(self.df.index, self.df['MA10'], label="ma10")
        plt.plot(self.df.index, self.df['flag'], label="flag")
        plt.legend()
        plt.show()


class Order(object):
    def __init__(self, name, trade_time, trade_type, asset_id, volume, price, commision, tax):
        self.name = name
        self.trade_time = trade_time
        self.trade_type = trade_type
        self.asset_id = asset_id
        self.volume = volume
        self.price = price
        self.commision = commision
        self.tax = tax
        self.cost = price * volume + commision + tax
        

class RiskManage(object):
    def __init__(self) -> None:
        pass

    def check(self, order):
        flag = True
        return flag

from libsql_utils.model.stock import formStock
from sqlalchemy import select

def order2sql(engine, order: Order):
    with Session(engine) as session:
        sql = formOrderSet(
            trader_name = order.name,
            trade_time = order.trade_time,
            trade_type = order.trade_type,
            asset_id = order.asset_id,
            volume = order.volume,
            price = order.price,
            commision = order.commision,
            tax = order.tax,
            cost = order.cost
            )
        session.add(sql)
        session.commit()


def SMA():
    eng = engine_init('localhost', 'root', '6414939', 'stock')
    eng2 = engine_init('localhost', 'root', '6414939', 'trade')
    remote = engine_init('115.159.1.221', 'root', '6414939', 'stock')
    d = get_n_day_before_date(eng, 'SH600000', '2000-1-1', 50)
    # 策略运行
    df = DataFrame(d, columns=['trade_date', 'open', 'close', 'high', 'low'])
    df.set_index('trade_date', inplace=True)
    strategy = StrategyBase(df)
    for idx in strategy.index:
        if strategy.step(idx):
            order = Order('John', datetime.now(), 's', 'SZ300015', 300, 25.7, 3.5, 2.5)
        else:
            pass
        order2sql(eng2, order)

if __name__ == '__main__':
    from datetime import datetime
    from pandas import Timestamp
    eng = engine_init('115.159.1.221', 'root', '6414939', 'stock')
    # 调用数据
    d = get_n_day_before_date(eng, 'SH600000', '2000-1-1', 50)
    # 策略运行
    df = DataFrame(d, columns=['trade_date', 'open', 'close', 'high', 'low'])
    df.set_index('trade_date', inplace=True)
    strategy = StrategyBase(df)
    for idx in strategy.index:
        print(idx if strategy.step(idx) else False)
    order = Order('John', datetime.now(), 's', 'SZ300015', 300, 25.7, 3.5, 2.5)
    eng2 = engine_init('localhost', 'root', '6414939', 'trade')
    order2sql(eng2, order)
    gen = TradeDate()
    g = gen.get_generator(eng)
    for i in g:
        print(i)