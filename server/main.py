import flask
import logging
import logging.handlers as handlers
from pathlib import Path
import json
import os
from pprint import pprint

LISTENING_PORT = 8080

formatter = logging.Formatter('%(asctime)s-%(levelname)s: %(message)s')
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
consoleHandler.setFormatter(formatter)
fileLogger = handlers.RotatingFileHandler("logs.log",maxBytes=1000000,backupCount=5)
fileLogger.setLevel(logging.DEBUG)
fileLogger.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(consoleHandler)
logger.addHandler(fileLogger)
logger.setLevel(logging.DEBUG)
app = flask.Flask(__name__)
stateFiles = {}

if os.path.isfile("storageState.json"):
    with open("storageState.json", "r") as f:
        stateFiles = json.loads(f.read())
    logger.info("Reloaded state from file")

def saveState():
    with open("storageState.json","w") as f:
        f.write(json.dumps(stateFiles))

@app.route('/storage/<name>/lock',methods=['LOCK','UNLOCK'])
def lockState(name):
    content = flask.request.get_json(silent=True)
    if flask.request.method == "LOCK":
        if stateFiles[name]["lock"]:
            return {"ID":stateFiles[name]["lock"]["ID"]},423
        else:
            stateFiles[name]["lock"] = content
            saveState()
            return {}, 200
    elif flask.request.method == "UNLOCK":
        stateFiles[name]["lock"] = False
        saveState()
        return {}, 200
            

@app.route('/storage/<name>', methods=['GET','POST','DELETE'])
def accessStorage(name):
    if flask.request.method == "GET":
        if name not in stateFiles:
            stateFiles[name] = {"file_location":f"states/{name}.tfstate","lock":False}
            with open(f"states/{name}.tfstate","w") as f:
                f.write(json.dumps({"version":1}))
            saveState()
            return {"version":1}, 200
        else:
            with open(f"states/{name}.tfstate","r") as f:
                data = json.loads(f.read())
            return data, 200
    elif flask.request.method == "POST":
        content = flask.request.get_json(silent=True)
        with open(f"states/{name}.tfstate","w") as f:
            f.write(json.dumps(content))
        return {}, 200
    elif flask.request.method == "DELETE":
        stateFiles.pop(name)
        os.remove(f"states/{name}.tfstate")
        return {}, 200

app.run(host='0.0.0.0',port=LISTENING_PORT)