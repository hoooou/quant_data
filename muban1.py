from datetime import datetime

import backtrader as bt  # 升级到最新版


# 创建策略继承bt.Strategy


class TestStrategy(bt.Strategy):
    params = (
        # 持仓够5个单位就卖出
        ('exitbars', 5),
    )

    def log(self, txt, dt=None):
        # 记录策略的执行日志
        dt = dt or self.datas[0].datetime.date(0)

    #         print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 保存收盘价的引用
        self.dataclose = self.datas[0].close
        # 跟踪挂单
        self.order = None
        # 买入价格和手续费
        self.buyprice = None
        self.buycomm = None

    # 订单状态通知，买入卖出都是下单
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # broker 提交/接受了，买/卖订单则什么都不做
            return

        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    '已买入, 价格: %.2f, 费用: %.2f, 佣金 %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('已卖出, 价格: %.2f, 费用: %.2f, 佣金 %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            # 记录当前交易数量
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/保证金不足/拒绝')

        # 其他状态记录为：无挂起订单
        self.order = None

    # 交易状态通知，一买一卖算交易
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('交易利润, 毛利润 %.2f, 净利润 %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # 记录收盘价
        self.log('Close, %.2f' % self.dataclose[0])

        # 如果有订单正在挂起，不操作
        if self.order:
            return

        # 如果没有持仓则买入
        if not self.position:
            # 今天的收盘价 < 昨天收盘价
            if self.dataclose[0] < self.dataclose[-1]:
                # 昨天收盘价 < 前天的收盘价
                if self.dataclose[-1] < self.dataclose[-2]:
                    # 买入
                    self.log('买入单, %.2f' % self.dataclose[0])
                    # 跟踪订单避免重复
                    self.order = self.buy()
        else:
            # 如果已经持仓，且当前交易数据量在买入后5个单位后
            # 此处做了更新将5替换为参数
            if len(self) >= (self.bar_executed + self.params.exitbars):
                # 全部卖出
                self.log('卖出单, %.2f' % self.dataclose[0])
                # 跟踪订单避免重复
                self.order = self.sell()


def startCereBro(cerebro, start_date, end_date, data):
    cerebro.adddata(data, "OK")  # 将数据传入回测系统
    cerebro.addstrategy(TestStrategy)  # 将交易策略加载到回测系统中
    start_cash = 1000000
    cerebro.broker.setcash(start_cash)  # 设置初始资本为 100000
    cerebro.broker.setcommission(commission=0.002)  # 设置交易手续费为 0.2%
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    results = cerebro.run(optreturn=True)  # 运行回测系统
    port_value = cerebro.broker.getvalue()  # 获取回测结束后的总资金
    pnl = port_value - start_cash  # 盈亏统计

    print(f"初始资金: {start_cash}")
    print(f"总资金: {round(port_value, 2)}")
    print(f"净收益: {round(pnl, 2)}")
    print(f"净收益率: {(round(pnl, 2) / start_cash) * 100}")
    return results


from utils.backUtils import *

def oneStratery():
        start_date = "20210101"  # 回测开始时间
        end_date = "20211101"  # 回测结束时间
        print(f"回测期间：{start_date}:{end_date}")
        stock_hfq_df = DataUtils.getData("000001", start_date, end_date)
        data = bt.feeds.PandasData(dataname=stock_hfq_df, fromdate=datetime.strptime(start_date, "%Y%m%d"),
                                   todate=datetime.strptime(end_date, "%Y%m%d"))  # 加载数据
        cerebro = bt.Cerebro()  # 初始化回测系统
        results = startCereBro(cerebro, start_date, end_date, data)
        BackUtils.showThreePlot(cerebro)


def optStratery():
    start_date = "20210101"  # 回测开始时间
    end_date = "20211101"  # 回测结束时间
    print(f"回测期间：{start_date}:{end_date}")
    stock_hfq_df = DataUtils.getData("000001", start_date, end_date)
    data = bt.feeds.PandasData(dataname=stock_hfq_df, fromdate=datetime.strptime(start_date, "%Y%m%d"),
                               todate=datetime.strptime(end_date, "%Y%m%d"))  # 加载数据
    cerebro = bt.Cerebro()  # 初始化回测系统
    results = startCereBro(cerebro, start_date, end_date, data)
    BackUtils.showThreePlot(cerebro)


if __name__ == '__main__':
    oneStratery()
