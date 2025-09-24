from flask import Flask, render_template, request
# pip install psutil flask-cors
import psutil
import os
import shutil
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Allowable processes
SAFE_TO_KILL = {
    "POWERPNT.EXE",
    "WINWORD.EXE",
    "EXCEL.EXE",
    "MSEDGE.EXE",
    "CHROME.EXE",
}

@app.route("/wipe")
def wipe():
    if not os.path.exists("E:/"):
        return "Unsuccesful"
    for item in os.listdir("E:/"):
        item_path = os.path.join("E:/", item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)
    return "Sucessful"

@app.route("/kill")
def kill():
    # read ?process=CHROME.EXE from query param
    proc_name = request.args.get("process", "").upper()
    if proc_name not in SAFE_TO_KILL:
        return f"Process '{proc_name}' not allowed", 400

    flag = False
    for p in psutil.process_iter(['pid', 'name']):
        try:
            if p.name().upper() == proc_name:
                p.terminate()
                p.wait(5)
                flag = True
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not flag:
        return f"Unsuccessful: '{proc_name}' not found"
    else:
        return f"Successful: killed '{proc_name}'"

@app.route("/")
def home():
    return render_template("index2.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
