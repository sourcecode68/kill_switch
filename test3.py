from flask import Flask,render_template
# pip install psutil
import psutil
import time
import os
import shutil
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

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
    SAFE_TO_KILL = {"POWERPNT.EXE", "WINWORD.EXE", "EXCEL.EXE"}
    flag=False
    for p in psutil.process_iter(['pid','name']): 
        if p.name().upper() in SAFE_TO_KILL:
            p.terminate()
            p.wait(5)
            flag=True
            break
    if(flag==False):
        return "Unseccessful"
    else:
        return "successful"
@app.route("/")
def home():

    return render_template("index.html")
if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0")
