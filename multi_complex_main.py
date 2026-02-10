import backtrader as bt
import os
from strategies.indicators_logic import ProTrendStrategy


def run_multi_backtest():
    cerebro = bt.Cerebro()
    # 注入优化后的双向策略参数
    cerebro.addstrategy(ProTrendStrategy, ema_p=30, atr_mult=1.8, risk=0.03)

    data_dir = 'data'
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

    for file in csv_files:
        data = bt.feeds.GenericCSVData(
            dataname=os.path.join(data_dir, file),
            dtformat='%Y-%m-%d', datetime=0, open=1, high=2, low=3, close=4, volume=5, openinterest=6,
            name=file.split('_')[0]
        )
        cerebro.adddata(data)

    cerebro.broker.setcash(200000.0)
    cerebro.broker.setcommission(commission=0.0001)
    cerebro.broker.set_coc(True)

    # 分析器
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='dd')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='ta')

    print("🚀 启动多品种 [多空双向] 组合回测...")
    strategies = cerebro.run()
    strat = strategies[0]

    # 结果展示
    final_v = cerebro.broker.getvalue()
    max_dd = strat.analyzers.dd.get_analysis().max.drawdown
    print("\n" + "=" * 40)
    print(f"📊 组合回测最终报告")
    print("-" * 40)
    print(f"期末净值: {final_v:.2f}")
    print(f"盈亏比例: {(final_v / 200000.0 - 1) * 100:.2f}%")
    print(f"最大回撤: {max_dd:.2f}%")
    print("=" * 40)

    # 绘图
    cerebro.plot(style='candle', volume=False)


if __name__ == "__main__":
    run_multi_backtest()