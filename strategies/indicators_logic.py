import backtrader as bt


class ProTrendStrategy(bt.Strategy):
    params = dict(
        ema_p=30,  # 趋势中轴
        atr_p=14,
        rsi_p=14,
        atr_mult=1.8,  # 通道宽度
        risk=0.05  # 既然回撤仅3%，我们将风险提高到5%以追求更高收益
    )

    def __init__(self):
        self.inds = {}
        for d in self.datas:
            self.inds[d] = {
                'ema': bt.ind.EMA(d.close, period=self.p.ema_p),
                'atr': bt.ind.ATR(d, period=self.p.atr_p),
                'rsi': bt.ind.RSI(d.close, period=self.p.rsi_p),
                'hi': 0.0, 'lo': 1000000.0
            }
            self.inds[d]['up'] = self.inds[d]['ema'] + self.p.atr_mult * self.inds[d]['atr']
            self.inds[d]['dn'] = self.inds[d]['ema'] - self.p.atr_mult * self.inds[d]['atr']

    def next(self):
        for d in self.datas:
            pos = self.getposition(d)
            ind = self.inds[d]

            if not pos:
                # 多头入场
                if d.close[0] > ind['up'][0] and ind['rsi'][0] > 50:
                    size = int((self.broker.get_value() * self.p.risk) / (ind['atr'][0] * 3 * 10))
                    if size >= 1:
                        self.buy(data=d, size=size)
                        ind['hi'] = d.close[0]
                # 空头入场
                elif d.close[0] < ind['dn'][0] and ind['rsi'][0] < 50:
                    size = int((self.broker.get_value() * self.p.risk) / (ind['atr'][0] * 3 * 10))
                    if size >= 1:
                        self.sell(data=d, size=size)
                        ind['lo'] = d.close[0]
            else:
                if pos.size > 0:  # 多头管理
                    ind['hi'] = max(ind['hi'], d.close[0])
                    # 价格跌破最高点回落的3倍ATR 或 跌破中轨
                    if d.close[0] < ind['hi'] - (3.0 * ind['atr'][0]) or d.close[0] < ind['ema'][0]:
                        self.close(data=d)
                elif pos.size < 0:  # 空头管理
                    ind['lo'] = min(ind['lo'], d.close[0])
                    # 价格突破最低点反弹的3倍ATR 或 突破中轨
                    if d.close[0] > ind['lo'] + (3.0 * ind['atr'][0]) or d.close[0] > ind['ema'][0]:
                        self.close(data=d)