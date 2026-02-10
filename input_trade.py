import json
import os

POS_FILE = "positions.json"


def load_pos():
    if os.path.exists(POS_FILE):
        with open(POS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}


def save_pos(pos_dict):
    with open(POS_FILE, "w", encoding="utf-8") as f:
        json.dump(pos_dict, f, indent=4, ensure_ascii=False)
    print(f"\n✅ 成功保存！当前实盘监控品种: {list(pos_dict.keys())}")


def main():
    while True:
        pos_dict = load_pos()
        print("\n" + "=" * 30)
        print("📊 实盘持仓管理工具")
        print("1. 录入/修改持仓")
        print("2. 删除/平仓品种")
        print("3. 查看当前实盘")
        print("4. 退出")
        choice = input("请选择操作 (1-4): ")

        if choice == '1':
            symbol = input("请输入品种代码 (如 RB0 或 I0): ").upper()
            side = input("持仓方向 (long/short): ").lower()
            if side not in ['long', 'short']:
                print("❌ 方向输入错误，只能填 long 或 short")
                continue
            price = float(input("成交均价: "))
            size = int(input("持仓手数: "))

            pos_dict[symbol] = {
                "side": side,
                "price": price,
                "size": size
            }
            save_pos(pos_dict)

        elif choice == '2':
            symbol = input("请输入要删除的品种代码: ").upper()
            if symbol in pos_dict:
                del pos_dict[symbol]
                save_pos(pos_dict)
                print(f"🗑️ 已移除 {symbol}")
            else:
                print("⚠️ 该品种不在持仓列表中")

        elif choice == '3':
            print("\n当前实盘记录:")
            print(json.dumps(pos_dict, indent=4, ensure_ascii=False))

        elif choice == '4':
            break


if __name__ == "__main__":
    main()