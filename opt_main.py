import backtrader as bt
import os
from strategies.indicators_logic import ProTrendStrategy


def run_optimization():
    cerebro = bt.Cerebro(maxcpus=None, optreturn=True)

    # 针对双向交易重新设定优化区间
    cerebro.optstrategy(
        ProTrendStrategy,
        ema_p=[20, 30, 40],
        atr_mult=[1.2, 1.8, 2.4]
    )

    data_path = 'data/RB0_history.csv'  # 以螺纹钢作为基准
    data = bt.feeds.GenericCSVData(
        dataname=data_path, dtformat='%Y-%m-%d',
        datetime=0, open=1, high=2, low=3, close=4, volume=5, openinterest=6
    )
    cerebro.adddata(data)

    cerebro.broker.setcash(100000.0)
    cerebro.addanalyzer(bt.analyzers.Returns, _name='ret')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='dd')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='ta')

    print("🚀 启动双向策略并行优化...")
    opt_results = cerebro.run()

    final_list = []
    for run in opt_results:
        for strat in run:
            ta = strat.analyzers.ta.get_analysis()
            t_count = ta.total.total if 'total' in ta else 0
            rtn = strat.analyzers.ret.get_analysis().get('rtot', 0)
            max_dd = strat.analyzers.dd.get_analysis().get('max', {}).get('drawdown', 0)
            final_list.append((strat.params.ema_p, strat.params.atr_mult, 100000 * (1 + rtn), max_dd, t_count))

    sorted_res = sorted(final_list, key=lambda x: x[2], reverse=True)
    print("\n" + "=" * 60)
    print(f"{'EMA':<5} | {'ATR':<5} | {'净值':<12} | {'回撤%':<8} | {'次数'}")
    print("-" * 60)
    for r in sorted_res:
        print(f"{r[0]:<5} | {r[1]:<5.1f} | {r[2]:<12.2f} | {r[3]:<8.2f} | {r[4]}")


if __name__ == "__main__":
    run_optimization()