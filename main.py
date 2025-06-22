from multiprocessing import Process
import time
import json
import os
from message import control_message
from gui_mode import control_gui_mode
from systerm_control_by_handgesture import system_control

MESSAGE_FILE_PATH = 'message.json'

def monitor_status(processes):
    while True:
        try:
            with open(MESSAGE_FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if str(data.get("status", "true")).lower() == "false":
                print("Nhận lệnh dừng từ message.json. Thoát toàn bộ chương trình.")
                # Đặt lại status = true trước khi thoát
                data['status'] = "true"
                with open(MESSAGE_FILE_PATH, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print("Đã đặt lại status = true trong message.json.")
                # Dừng tất cả process con
                for p in processes:
                    if p.is_alive():
                        p.terminate()
                break
        except Exception:
            pass
        time.sleep(1)

if __name__ == "__main__":
    p1 = Process(target=control_message)
    p2 = Process(target=control_gui_mode)
    p3 = Process(target=system_control)
    processes = [p1, p2, p3]

    for p in processes:
        p.start()

    monitor_status(processes)  # Chạy monitor ở main process

    for p in processes:
        p.join()

