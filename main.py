import requests
import time
import os
import json
import ctypes

apiURL = "https://inspirobot.me/api?generate=true"
appdata = os.getenv("APPDATA")
startUpFolder = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
downloadPath = os.path.join(appdata, "inspiroBackground", "background.jpg")
configPath = os.path.join(appdata, "inspiroBackground", "config.json")

interval = 60


def loadConfig():
    global interval
    if not os.path.exists(configPath):
        os.makedirs(os.path.dirname(configPath), exist_ok=True)
        with open(configPath, "w") as configFile:
            json.dump({"interval": 60}, configFile)
    else:
        with open(configPath, "r") as configFile:
            config = json.load(configFile)
            interval = config["interval"]


def setBackground():
    # get image url
    imgURL = requests.get(apiURL).text
    # download image
    img = requests.get(imgURL)
    with open(downloadPath, "wb") as imgFile:
        imgFile.write(img.content)
    # set background
    absolutePath = os.path.abspath(downloadPath)
    ctypes.windll.user32.SystemParametersInfoW(20, 0, absolutePath, 0)


if __name__ == "__main__":
    loadConfig()
    while True:
        setBackground()
        print("Background set.")
        time.sleep(interval)
