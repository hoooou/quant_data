from backtrader_plotting import Bokeh


class BackUtils:
    def openQuantStats(results):
        import warnings
        warnings.filterwarnings('ignore')
        result = results[0]
        portfolio_stats = result.analyzers.getbyname('pyfolio')
        returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
        returns.index = returns.index.tz_convert(None)
        import matplotlib.pyplot as plt
        # % matplotlib inline
        plt.rcParams['font.sans-serif'] = ['Heiti TC']
        plt.rcParams['axes.unicode_minus'] = False
        import quantstats
        returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
        returns.index = returns.index.tz_convert(None)
        quantstats.reports.html(returns, output='stats.html', title='Stock Sentiment')

        import webbrowser
        import os
        cwd = os.getcwd()
        filename = "file://" + cwd + "/stats.html"
        webbrowser.open_new_tab(filename)

    def showThreePlot(cerebro):
        b = Bokeh(style='bar')
        cerebro.plot(b)

    def showSystemPlot(cerebro):
        cerebro.plot()


class DataUtils:
    def getStockData(code, start_date, end_date):
        import akshare as ak  # 升级到最新版
        import pandas as pd

        # 利用 AKShare 获取股票的后复权数据，这里只获取前 6 列
        stock_hfq_df = ak.stock_zh_a_hist(symbol=code, adjust="hfq", start_date=start_date, end_date=end_date).iloc[:,
                       :6]
        # 处理字段命名，以符合 Backtrader 的要求
        stock_hfq_df.columns = [
            'date',
            'open',
            'close',
            'high',
            'low',
            'volume',
        ]
        # 把 date 作为日期索引，以符合 Backtrader 的要求
        stock_hfq_df.index = pd.to_datetime(stock_hfq_df['date'])
        return stock_hfq_df

    def getZhishu(code="sz399552"):
        import akshare as ak
        import pandas as pd

        stock_zh_index_daily_df = ak.stock_zh_index_daily(symbol=code)
        # 把 date 作为日期索引，以符合 Backtrader 的要求
        stock_zh_index_daily_df.index = pd.to_datetime(stock_zh_index_daily_df['date'])
        stock_zh_index_daily_df.to_csv("stock.csv")
        return stock_zh_index_daily_df;

    def getEtfData(code="512480"):
        import pandas as pd
        import efinance as ef
        stock_hfq_df=ef.stock.get_quote_history(code).iloc[:,2:8]
        stock_hfq_df.columns = [
            'date',
            'open',
            'close',
            'high',
            'low',
            'volume',
        ]
        stock_hfq_df.index = pd.to_datetime(stock_hfq_df['date'])
        stock_hfq_df.to_csv("getEtfData.csv")
        if stock_hfq_df.empty:
            raise Exception("数据为空")
        return stock_hfq_df



if __name__ == '__main__':
    DataUtils.getEtfData(code='510350').to_csv("getEtfData.csv")
    # DataUtils.getStockData("300750", "20210101", "20211101").to_csv("stock.csv")
