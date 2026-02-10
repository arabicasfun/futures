import shutil
import os
import datetime


def backup_files():
    # 1. 定义需要备份的文件
    target_files = ["config.json", "positions.json"]
    # 2. 定义备份目录
    backup_dir = "backups"

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"📁 已创建备份文件夹: {backup_dir}")

    # 3. 获取当前时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    for file in target_files:
        if os.path.exists(file):
            # 生成新的文件名，例如: config_20260210_160000.json
            new_name = f"{file.split('.')[0]}_{timestamp}.json"
            dest_path = os.path.join(backup_dir, new_name)

            # 执行复制
            shutil.copy2(file, dest_path)
            print(f"✅ 已备份: {file} -> {dest_path}")
        else:
            print(f"⚠️ 警告: 未找到文件 {file}，跳过。")


if __name__ == "__main__":
    backup_files()