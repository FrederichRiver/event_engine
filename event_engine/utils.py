from sqlalchemy.orm import Session
from libsql_utils.model.stock import formStock
from sqlalchemy import select

class TradeDate(object):
    def get_generator(self, engine):
        with Session(engine) as session:
            formStock.__table__.name = 'SH000001'
            sql = select(formStock.trade_date)
            result = session.execute(sql).all()
            g = (i[0] for i in result)
        return g
