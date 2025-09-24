from flask import Flask, render_template, request
# pip install psutil
import psutil
import os
import shutil
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/wipe")
def wipe():
    drive = request.args.get("drive", "E")  # default E if not provided
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
    return render_template("index3.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
