import requests
import time
import os
import json
import ctypes
import pystray
from PIL import Image
import threading

iconUrl = "https://inspirobot.me/website/images/inspirobot-dark-green.png"

apiURL = "https://inspirobot.me/api?generate=true"
appdata = os.getenv("APPDATA")
startUpFolder = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
downloadPath = os.path.join(appdata, "inspiroBackground", "background.jpg")
configPath = os.path.join(appdata, "inspiroBackground", "config.json")

interval = 60
iconImage = Image.open(requests.get(iconUrl, stream=True).raw)
running = True


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


def saveConfig():
    with open(configPath, "w") as configFile:
        json.dump({"interval": interval}, configFile)


def setInterval(newInterval):
    global interval
    interval = newInterval
    saveConfig()


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


def end():
    icon.stop()
    global running
    running = False


def isCustomInterval(x):
    return interval not in [30, 300, 600, 900, 1800]


icon = pystray.Icon("InspiroBackground", icon=iconImage)
icon.menu = pystray.Menu(
    pystray.MenuItem("New Background", setBackground),
    # submenu to set interval
    pystray.MenuItem("Set interval",
                     pystray.Menu(
                         pystray.MenuItem("30 seconds", lambda: setInterval(30), checked=lambda x: interval == 30),
                         pystray.MenuItem("1 minute", lambda: setInterval(300), checked=lambda x: interval == 300),
                         pystray.MenuItem("5 minutes", lambda: setInterval(600), checked=lambda x: interval == 600),
                         pystray.MenuItem("10 minutes", lambda: setInterval(900), checked=lambda x: interval == 900),
                         pystray.MenuItem("15 minutes", lambda: setInterval(1800), checked=lambda x: interval == 1800),
                         pystray.MenuItem("Custom", lambda: os.startfile(os.path.abspath(configPath)),
                                          checked=isCustomInterval),
                     )
                     ),
    pystray.MenuItem("Reload config", loadConfig),
    pystray.MenuItem("Run at startup (put exe in the folder)", lambda: os.startfile(os.path.abspath(startUpFolder))),
    pystray.MenuItem("Exit", end)
)


def loop():
    loadConfig()
    while running:
        try:
            setBackground()
        except Exception as e:
            print(e)
            time.sleep(5)
        lastTime = time.time()
        while time.time() - lastTime < interval and running:
            time.sleep(1)


thread = threading.Thread(target=loop)
thread.start()
icon.run()
