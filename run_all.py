import subprocess
import datetime
import requests
import json
import sys
import os

# ================= 配置区 =================
CONFIG_FILE = "config.json"


def load_webhook():
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ 错误：找不到配置文件 {CONFIG_FILE}")
        return None
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        try:
            config = json.load(f)
            return config.get("dingtalk_webhook")
        except Exception as e:
            print(f"❌ 配置文件解析失败: {e}")
            return None


def send_ding(content):
    webhook_url = load_webhook()
    if not webhook_url: return

    headers = {"Content-Type": "application/json"}
    payload = {
        "msgtype": "markdown",
        "markdown": {
            # 这里的 title 加入了“信号”关键词，以匹配你的机器人设置
            "title": "期货交易信号预报",
            "text": f"### 🔔 自动化信号预报\n**时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n{content}"
        },
        "at": {"isAtAll": False}
    }

    try:
        resp = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
        print(f"钉钉返回结果: {resp.text}")  # 打印结果方便调试
    except Exception as e:
        print(f"❌ 推送异常: {e}")


def run_script(py_file):
    print(f"▶️ 正在启动: {py_file}...")
    res = subprocess.run([sys.executable, py_file], capture_output=True, text=True, encoding='utf-8', errors='ignore')
    return res.stdout + "\n" + res.stderr


def main():
    # 执行流程
    run_script("getdata_pro.py")
    signal_log = run_script("daily_signal.py")

    if "--- 明日交易指令清单 ---" in signal_log:
        core_msg = signal_log.split("--- 明日交易指令清单 ---")[-1].strip()
        if core_msg:  # 确保有文字内容才发送
            send_ding(core_msg)
            print("✅ 信号已尝试推送到钉钉")
        else:
            print("💤 今日无具体操作信号，暂不推送")
    else:
        print("❌ 未在输出中找到清单标记，请检查 daily_signal.py")


if __name__ == "__main__":
    main()