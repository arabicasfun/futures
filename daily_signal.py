import backtrader as bt
import os
import re
import json
from strategies.indicators_logic import ProTrendStrategy


def load_real_positions():
    path = "positions.json"
    if not os.path.exists(path): return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {}


def get_multiplier(symbol):
    prefix = re.findall(r'[A-Z]+', symbol.upper())[0]
    multipliers = {'RB': 10, 'HC': 10, 'I': 100, 'J': 100, 'JM': 60, 'M': 10, 'AU': 1000}
    return multipliers.get(prefix, 10)


def generate_signals():
    try:
        real_pos = load_real_positions()
        cerebro = bt.Cerebro()
        cerebro.addstrategy(ProTrendStrategy, ema_p=30, atr_mult=1.8, risk=0.05)

        data_dir = 'data'
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        for file in csv_files:
            data = bt.feeds.GenericCSVData(
                dataname=os.path.join(data_dir, file), dtformat='%Y-%m-%d',
                datetime=0, open=1, high=2, low=3, close=4, volume=5, openinterest=6,
                name=file.split('_')[0]
            )
            cerebro.adddata(data)

        results = cerebro.run()
        strat = results[0]

        print("\n--- 明日交易指令清单 ---")

        for d in strat.datas:
            ind = strat.inds[d]
            curr_price = d.close[0]
            name = d._name
            mult = get_multiplier(name)
            ema_val = ind['ema'][0]

            if name in real_pos:
                p = real_pos[name]
                side = p['side']
                cost = p['price']

                # 计算盈亏
                if side == "long":
                    pnl_pct = (curr_price / cost - 1) * 100
                    pnl_val = (curr_price - cost) * p['size'] * mult
                    is_strategy_out = curr_price < ema_val  # 多单跌破中轨
                else:
                    pnl_pct = (cost / curr_price - 1) * 100
                    pnl_val = (cost - curr_price) * p['size'] * mult
                    is_strategy_out = curr_price > ema_val  # 空单突破中轨

                # --- 预警逻辑判断 ---
                alert_msg = ""
                if pnl_pct <= -5.0:
                    alert_msg = " ⚠️【风控警告：亏损超5%】"
                elif is_strategy_out:
                    alert_msg = " 🚨【策略警告：趋势破位平仓】"

                icon = "💰" if pnl_val >= 0 else "📉"
                prefix = "‼️" if alert_msg else icon

                print(f"{prefix} 【实盘】{name}: {side} 成本:{cost} 盈亏:{pnl_pct:.2f}% ({pnl_val:.0f}元){alert_msg}")
                print(f"   ∟ 当前价格:{curr_price:.1f} | 止损参考线:{ema_val:.1f}")

            else:
                # 信号判定逻辑 (保持不变)
                up, dn = ind['up'][0], ind['dn'][0]
                if curr_price > up and d.close[-1] <= ind['up'][-1]:
                    print(f"🔥 【新信号】{name}: 向上突破！")
                elif curr_price < dn and d.close[-1] >= ind['dn'][-1]:
                    print(f"🔥 【新信号】{name}: 向下突破！")
                else:
                    pass  # 观望品种不再详细打印

    except Exception as e:
        print(f"ERROR: {str(e)}")


if __name__ == "__main__":
    generate_signals()