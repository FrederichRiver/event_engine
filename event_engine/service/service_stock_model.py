def service_init_stock_model():
    
    pass


#!/usr/bin/python3

from libsql_utils.model.stock import formStock, formStockManager
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from pandas import DataFrame
from dev_global.path import CONF_FILE
from libutils.utils import read_url
import requests
import datetime
from finance_model.stock_list import get_stock_list2, get_index_list2
from tarantula.generator.netease_generator import StockGenerator
from tarantula.downloader.stock_data_downloader import StockDataDownloader
from redis import StrictRedis
from tarantula.parser.stock_data_parser import stock_name_parser, index_name_parser
from basic_util.log import dlog
import time
import random


# 将来转移到libutils里面
def get_now():
    return datetime.now()

# 创建stock_manager表
def service_create_stock_manager_table(engine):
    """
    创建空白的stock_manager表格
    """
    with Session(engine) as session:
        if not formStockManager.__table__.exists(engine):
            formStockManager.__table__.create(engine)
        session.commit()

def service_build_data_in_stock_manager(engine):
    # 获取股票列表
    # 判断股票代码是否在？
    # 在的话就在stock_manager当中创建记录
    pass
    #stock_list = get_stock_list()
    #event = EventTradeDataManager(GLOBAL_HEADER)
    # for stock_code in stock_list:
    #     if event.stock_exist(stock_code, )

# 从空白初始化所有股票表


def net_ease_code(stock_code):
    """
    input: SH600000, return: 0600000\n;
    input: SZ000001, return: 1000001.
    """
    if isinstance(stock_code, str):
        if stock_code[:2] == 'SH':
            stock_code = '0' + stock_code[2:]
        elif stock_code[:2] == 'SZ':
            stock_code = '1' + stock_code[2:]
        else:
            stock_code = None
    else:
        stock_code = None
    return stock_code

URL = read_url('URL_163_MONEY', CONF_FILE)

def url_netease(url, stock_code, start_date, end_date) -> str:
    query_code = net_ease_code(stock_code)
    netease_url = url.format(query_code, start_date, end_date)
    return netease_url


def service_init_stock_data(engine):
    """
    used when first time download stock data.
    """
    # 初始化redis连接，清空stock_table
    s = StrictRedis(db=1, decode_responses=True)
    s.delete('stock_table')
    # 运行stock list程序生成stock_list
    stock_list = get_stock_list2()
    # 将url写入redis
    stock_gene = StockGenerator()
    urls = stock_gene.run(stock_list)
    stock_gene.set_value(urls, db=1, key='stock_table')
    d = StockDataDownloader()
    insp = inspect(engine)
    with Session(engine) as session:
        # 从redis中提取url并下载数据
        while url:=s.brpop('stock_table', 5):
            time.sleep(random.randint(0, 5))
            df = d.download(url[1])
            if not df.empty:
                event_create_stock_table(engine, insp, session, df)

@dlog
def event_create_stock_table(engine, insp: inspect, session: Session, df: DataFrame):
    # 根据下载数据提取stock_code和stock_name
    stock_code, stock_name = stock_name_parser(df)
    if not insp.has_table(stock_code):
        print(f"{stock_code},{stock_name}")
        # 如果有stock_code没在stock_manager中就创建table
        formStock.__table__.name = stock_code
        formStock.__table__.create(engine)
        # 更新stock_manager
        stock_table = formStockManager(
            stock_code=stock_code,
            stock_name=stock_name,
            create_date=datetime.date.today(),
            )
        session.add(stock_table)
        session.commit()

# 因为index的更新很少，因此单独列出
def service_init_index_data(engine):
    """
    used when first time download index data.
    """
    # 初始化redis连接，清空stock_table
    s = StrictRedis(db=1, decode_responses=True)
    s.delete('index_table')
    # 运行stock list程序生成stock_list
    stock_list = get_index_list2()
    # 将url写入redis
    stock_gene = StockGenerator()
    urls = stock_gene.run(stock_list)
    stock_gene.set_value(urls, db=1, key='index_table')
    d = StockDataDownloader()
    insp = inspect(engine)
    with Session(engine) as session:
        # 从redis中提取url并下载数据
        while url:=s.brpop('index_table', 5):
            time.sleep(random.randint(0, 5))
            df = d.download(url[1])
            if not df.empty:
                event_create_index_table(engine, insp, session, df)


@dlog
def event_create_index_table(engine, insp: inspect, session: Session, df: DataFrame):
    # 根据下载数据提取stock_code和stock_name
    stock_code, stock_name = index_name_parser(df)
    # print(f"{stock_code},{stock_name}")
    if not insp.has_table(stock_code):
        # 如果有stock_code没在stock_manager中就创建table
        formStock.__table__.name = stock_code
        formStock.__table__.create(engine)
        # 更新stock_manager
        stock_table = formStockManager(
            stock_code=stock_code,
            stock_name=stock_name,
            create_date=datetime.date.today(),
            )
        session.add(stock_table)
        session.commit()


# 创建stock表

# 检索录入A股信息，并创建stock表

# 检索录入港股信息和美股信息

