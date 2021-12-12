from datetime import datetime

import backtrader as bt  # 升级到最新版


# 创建策略继承bt.Strategy


class MyStrategy(bt.Strategy):
    """
    主策略程序
    """
    params = (("maperiod", 7),("macd1", 7),("macd2", 7),("macds", 7),
              ('printlog', False),)  # 全局设定交易策略的参数, maperiod是 MA 均值的长度

    def __init__(self):
        """
        初始化函数
        """
        self.data_close = self.datas[0].close  # 指定价格序列
        # 初始化交易指令、买卖价格和手续费
        self.order = None
        self.buy_price = None
        self.buy_comm = None
        # 添加移动均线指标
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod
        )
        above_sma = self.data.close > self.sma
        below_sma = self.data.close <= self.sma

        self.MACD = bt.indicators.MACD(self.data, period_me1=self.params.macd1,period_me2=self.params.macd2,period_signal=self.params.macds)
        macd = self.MACD.macd
        signal = self.MACD.signal
        histo = bt.indicators.MACDHisto(self.data)

        # 收盘价大于histo，买入
        macd_buy = bt.And(macd > 0, signal > 0, histo > 0)
        # 收盘价小于等于histo，卖出
        macd_sell = bt.And(macd <= 0, signal <= 0, histo <= 0)

        self.buy_signal = bt.And(above_sma, macd_buy)
        self.sell_signal = bt.And(below_sma, macd_sell)

    def notify_cashvalue(self, cash, value):
        self.cash = cash;
        self.value = value;

    def next(self):
        """
        主逻辑
        """

        # self.log(f'收盘价, {data_close[0]}')  # 记录收盘价
        if self.order:  # 检查是否有指令等待执行,
            return
        # 检查是否持仓
        # self.log("仓位:%s" % (self.position))
        if not self.position:  # 没有持仓
            # 执行买入条件判断：收盘价格上涨突破15日均线
            if self.data_close[0] > self.sma[0]:
                # 执行买入
                size = self.cash * 0.8 / self.data_close[0];
                size = round(size, 0)
                self.log("BUY CREATE, %.2f,%d" % (self.data_close[0], size))
                self.order = self.buy(size=size)
        else:
            # 执行卖出条件判断：收盘价格跌破15日均线
            if self.data_close[0] < self.sma[0]:
                self.log("SELL CREATE, %.2f,%d" % (self.data_close[0], self.position.size))
                # 执行卖出
                self.order = self.sell(size=self.position.size)

    def log(self, txt, dt=None, do_print=False):
        """
        Logging function fot this strategy
        """
        if self.params.printlog or do_print:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        """
        记录交易执行情况
        """
        # 如果 order 为 submitted/accepted,返回空
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 如果order为buy/sell executed,报告价格结果
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f"买入:\n价格:{order.executed.price},\
                成本:{order.executed.value},\
                手续费:{order.executed.comm}"
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(
                    f"卖出:\n价格：{order.executed.price},\
                成本: {order.executed.value},\
                手续费{order.executed.comm}"
                )
            self.bar_executed = len(self)

            # 如果指令取消/交易失败, 报告结果
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("交易失败")
        self.order = None

    def notify_trade(self, trade):
        """
        记录交易收益情况
        """
        if not trade.isclosed:
            return
        self.log(f"策略收益：\n毛收益 {trade.pnl:.2f}, 净收益 {trade.pnlcomm:.2f}")

    def stop(self):
        """
        回测结束后输出结果
        """
        self.log("\n(MA均线： %2d日),(MACD1： %2d),(MA2： %2d日),(MA_SIGN： %2d日) 期末总资金 %.2f" % (self.params.maperiod,self.params.macd1,self.params.macd2,self.params.macds, self.broker.getvalue()), do_print=True)


def startCereBro(cerebro, data, optParams=None,macdParams=None):
    cerebro.adddata(data, "OK")  # 将数据传入回测系统
    if (optParams != None):
        cerebro.optstrategy(MyStrategy,maperiod=range(3, 31),macd1=range(3, 31),macd2=range(3, 31),macds=range(3, 31))  # 将交易策略加载到回测系统中
    else:
        cerebro.addstrategy(MyStrategy)  # 将交易策略加载到回测系统中
    start_cash = 1000
    cerebro.broker.setcash(start_cash)  # 设置初始资本为 100000
    cerebro.broker.setcommission(commission=0.002)  # 设置交易手续费为 0.2%
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)  # 设置买入数量
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    #runonce=False
    results = cerebro.run(maxcpus=100)  # 运行回测系统
    port_value = cerebro.broker.getvalue()  # 获取回测结束后的总资金
    pnl = port_value - start_cash  # 盈亏统计

    print(f"初始资金: {start_cash}")
    print(f"总资金: {round(port_value, 2)}")
    print(f"净收益: {round(pnl, 2)}")
    print(f"净收益率: {round(pnl / start_cash * 100, 3)}")
    return results


from utils.backUtils import *


def oneStratery(code, start_date, end_date):
    print(f"回测期间：{start_date}:{end_date}")
    # stock_hfq_df = DataUtils.getStockData("312480", start_date, end_date)
    # stock_hfq_df = DataUtils.getZhishu(code="sh312480")
    stock_hfq_df = DataUtils.getEtfData(code=code)
    data = bt.feeds.PandasData(dataname=stock_hfq_df, fromdate=datetime.strptime(start_date, "%Y%m%d"),
                               todate=datetime.strptime(end_date, "%Y%m%d"))  # 加载数据
    cerebro = bt.Cerebro()  # 初始化回测系统
    results = startCereBro(cerebro, data)
    BackUtils.showFourPlot(cerebro)


def optStratery(code, start_date, end_date):
    print(f"回测期间：{start_date}:{end_date}")
    # stock_hfq_df = DataUtils.getStockData("300750", start_date, end_date)
    # stock_hfq_df = DataUtils.getZhishu("sh312480")
    stock_hfq_df = DataUtils.getEtfData(code=code)
    data = bt.feeds.PandasData(dataname=stock_hfq_df, fromdate=datetime.strptime(start_date, "%Y%m%d"),
                               todate=datetime.strptime(end_date, "%Y%m%d"))  # 加载数据
    cerebro = bt.Cerebro()  # 初始化回测系统

    startCereBro(cerebro, data, range(3, 31),range(3, 31));
    # BackUtils.showThreePlot(cerebro)


if __name__ == '__main__':
    start_date = "20171201"  # 回测开始时间
    end_date = "20180601"  # 回测结束时间
    code = "512880";
    optStratery(code, start_date, end_date)
