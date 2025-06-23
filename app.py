from flask import Flask
from main import main as main_func
from google_drive_tools import main as drive_func

app = Flask(__name__)

@app.route("/run-main", methods=["GET"])
def call_main():
    return main_func()

@app.route("/run-drive", methods=["GET"])
def call_drive():
    return drive_func()

@app.route("/", methods=["GET"])
def home():
    return "Cloud Run is working! Use /run-main or /run-drive to trigger."
