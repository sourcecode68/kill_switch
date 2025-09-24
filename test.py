# pip install psutil
import psutil
import time
import os
import shutil

def kill_processes_holding_path(path, timeout=5):
    """Return number of processes killed."""
    killed = 0
    for p in psutil.process_iter(['pid','name']):
        try:
            for f in p.open_files():
                # exact match
                if os.path.normcase(f.path) == os.path.normcase(path):
                    print(f"Found {path} held by pid={p.pid} name={p.name()}; terminating...")
                    p.terminate()  # polite
                    try:
                        p.wait(timeout)
                    except psutil.TimeoutExpired:
                        print("Process didn't exit; killing...")
                        p.kill()
                    killed += 1
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return killed

def wipe_pendrive(drive_path):
    for item in os.listdir(drive_path):
        item_path = os.path.join(drive_path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except PermissionError as e:
            print("PermissionError for", item_path, e)
            # try to free handle and retry
            killed = kill_processes_holding_path(item_path)
            if killed:
                # try again
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e2:
                    print("Still failed after killing:", e2)
                    return False
            else:
                return False
    return True

# usage
if __name__ == "__main__":
    import time
    while True:
        if os.path.exists("E:\\"):
            if wipe_pendrive("E:\\"):
                print("Wiped.")
                break
        time.sleep(10)
