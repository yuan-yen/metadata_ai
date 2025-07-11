import os
import shutil
import time
import subprocess
from datetime import datetime

# ====== 設定 ======
SOURCE_FILE = '/your/path_a/your_file.txt'  # 修改為來源檔案的完整路徑
DEST_FILE = './your_file.txt'               # 目標檔案名稱（存在當前目錄）
INTERVAL = 20                               # 秒數

def git_commit_and_push():
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"Update at {timestamp}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        subprocess.run(['git', 'push'], check=True)
        print(f"[{timestamp}] Commit & Push 成功")
    except subprocess.CalledProcessError as e:
        print(f"[{datetime.now()}] Git 錯誤: {e}")

def loop_copy_and_push():
    while True:
        try:
            #shutil.copy2(SOURCE_FILE, DEST_FILE)
            #print(f"[{datetime.now()}] 檔案已複製")
            git_commit_and_push()
        except Exception as e:
            print(f"[{datetime.now()}] 發生錯誤: {e}")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    loop_copy_and_push()