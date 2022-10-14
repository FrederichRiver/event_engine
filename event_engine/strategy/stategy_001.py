#!/usr/bin/python3

from email import header
from wsgiref import headers
from libsql_utils.engine import engine_init
from libsql_utils.model.stock import formStockManager, get_formStock
from sqlalchemy import select
from sqlalchemy.orm import Session
from pandas import DataFrame
import datetime

def strategy_001():
    eng = engine_init(host='localhost', acc='stock', pw='stock2020', db='stock')
    session = Session(eng)
    # 获取 stock_list
    query = select(formStockManager.stock_code).where(formStockManager.flag=='s').where(formStockManager.update_date=='2022-10-13')
    result = session.execute(query).all()
    stock_list = []
    for item in result:
        stock_list.append(item[0])
    # 逐个分析
    col = ['trade_date', 'close', 'high', 'low', 'open', 'amplitude']

    for stock in stock_list:
        formStock = get_formStock(stock)
        query = select(
            formStock.trade_date,
            formStock.close_price,
            formStock.high_price,
            formStock.low_price,
            formStock.open_price,
            formStock.amplitude
            )
        result = session.execute(query).fetchmany(40)
        df =  DataFrame(result, columns=col)
        flag = "False"
        if df is not None:
            df.set_index('trade_date', inplace=True)
            for i in [5, 10, 20]:
                df[f"MA{i}"] = df['close'].rolling(i).mean()
            row = df.iloc[-1:,]
            row['MA20'] = row['MA20'] / row['MA5']
            row['MA10'] = row['MA10'] / row['MA5']
            row['MA5'] = 1.0
            # print(row)
            if row.index == datetime.date(2022, 10, 13):
                if row['MA5'].values[0] < row['MA10'].values[0] < row['MA20'].values[0]:
                    flag = "True"
                    with open('/home/fred/Documents/dist/check.txt', 'a') as f:
                        f.write(f"{stock}: {flag}\n")
                    # 将代码写入redis数据库
            else:
                flag = 'False'
        print(f"{stock}: {flag}")
        # with open('/home/fred/Documents/dist/check.txt', 'a') as f:
        #     f.write(f"{stock}: {flag}\n")

# 第二版将这种判断改为卷积计算。
# 需要收集大数据，建立数据集
# 训练模型
# 生成卷积核

if __name__ == '__main__':
    strategy_001()