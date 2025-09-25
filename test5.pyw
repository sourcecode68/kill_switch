from flask import Flask, render_template, request
import psutil
import os
import shutil
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
doc="""
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
        max-width: 560px;
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
      input[type="text"] {
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
      button {
        flex: 1;
        padding: 12px;
        border-radius: 10px;
        border: 0;
        font-weight: 600;
        cursor: pointer;
      }
      .kill {
        background: #f7b267;
      }
      .wipe {
        background: #ef476f;
        color: white;
      }
      .status {
        margin-top: 12px;
        padding: 10px;
        border-radius: 8px;
        background: #f1f5f9;
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
      <h1>Remote Kill & Wipe</h1>
      <p>
        Use this page to call your Flask endpoints. Make sure the Flask server
        is running and you are authorised to control the target machine.
      </p>

      <label for="processSelect">Select Process to Kill</label>
      <select id="processSelect">
        <option value="POWERPNT.EXE">PowerPoint</option>
        <option value="WINWORD.EXE">Word</option>
        <option value="EXCEL.EXE">Excel</option>
        <option value="MSEDGE.EXE">Microsoft Edge</option>
        <option value="CHROME.EXE">Google Chrome</option>
      </select>

      <label for="driveSelect">Select Drive to Wipe</label>
      <select id="driveSelect">
        <option value="E">E:</option>
        <option value="F">F:</option>
        <option value="G">G:</option>
      </select>

      <div class="row">
        <button id="killBtn" class="kill">Kill (terminate apps)</button>
        <button id="wipeBtn" class="wipe">Wipe (erase drive)</button>
      </div>

      <div class="status" id="status">Ready.</div>
    </div>

    <script>
      const killBtn = document.getElementById("killBtn");
      const wipeBtn = document.getElementById("wipeBtn");
      const status = document.getElementById("status");
      const processSelect = document.getElementById("processSelect");
      const driveSelect = document.getElementById("driveSelect");
      const base = window.location.origin;

      async function callEndpoint(path) {
        const url = base.replace(/\/$/, "") + path;
        setButtonsDisabled(true);
        status.textContent = "Calling " + url + " ...";
        try {
          const resp = await fetch(url, { method: "GET", credentials: "omit" });
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
      function setButtonsDisabled(v) {
        killBtn.disabled = v;
        wipeBtn.disabled = v;
        killBtn.style.opacity = v ? "0.6" : "1";
        wipeBtn.style.opacity = v ? "0.6" : "1";
      }

      killBtn.addEventListener("click", async () => {
        const processName = processSelect.value;
        await callEndpoint("/kill?process=" + encodeURIComponent(processName));
      });

      wipeBtn.addEventListener("click", async () => {
        const drive = driveSelect.value;
        await callEndpoint("/wipe?drive=" + encodeURIComponent(drive));
      });
    </script>
  </body>
</html>
"""
@app.route("/wipe")
def wipe():
    drive = request.args.get("drive", "E")
    path = f"{drive}:/"
    if not os.path.exists(path):
        return "Unsuccesful"
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
        "CHROME.EXE"
    }
    process_to_kill = request.args.get("process", "").upper()
    if process_to_kill not in SAFE_TO_KILL:
        return "Invalid or unsafe process"
    flag = False
    for p in psutil.process_iter(['pid','name']): 
        if p.info['name'] and p.info['name'].upper() == process_to_kill:
            p.terminate()
            p.wait(5)
            flag = True
    if not flag:
        return "Unsuccessful"
    else:
        return f"Successfully killed {process_to_kill}"
@app.route("/")
def home():
    return doc
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")