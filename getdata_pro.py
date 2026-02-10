import akshare as ak
import pandas as pd
import os
import time


def fetch_all(symbols=["RB0", "I0", "HC0", "J0"], start_date="20210101"):
    """
    start_date: 设置为 20210101 获取 5 年数据
    """
    if not os.path.exists('data'):
        os.makedirs('data')

    for symbol in symbols:
        try:
            print(f"正在同步 {symbol} 历史数据 (起始日期: {start_date})...")

            # 使用新浪接口获取日线数据
            df = ak.futures_zh_daily_sina(symbol=symbol)

            # 字段处理
            df['date'] = pd.to_datetime(df['date'])
            df = df.rename(columns={'date': 'datetime', 'hold': 'open_interest'})

            # 过滤日期范围
            df = df[df['datetime'] >= pd.to_datetime(start_date)]
            df = df.sort_values('datetime')

            # 检查是否有数据
            if df.empty:
                print(f"⚠️ {symbol} 在此日期范围内无数据")
                continue

            # 保存为标准 CSV
            file_path = f"data/{symbol}_history.csv"
            df.to_csv(file_path, index=False)
            print(f"✅ {symbol} 同步成功，共 {len(df)} 行记录")

            # 避免请求过快
            time.sleep(1)

        except Exception as e:
            print(f"❌ {symbol} 抓取失败: {e}")


if __name__ == "__main__":
    # 获取过去 5 年数据
    fetch_all(start_date="20210101")