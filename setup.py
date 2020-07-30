import json
import os
import png
import pyqrcode
import socket
import time
from threading import Thread

SETTINGS_PATH = os.path.abspath('settings.json')
START_PATH = os.path.abspath('start.py')
QR_PATH = os.path.abspath('qr.png')

def main():
    with open(SETTINGS_PATH, 'r') as f:
        settings = json.load(f)

    if not settings['app_is_connected']:
        ip = getIP()
        qr = pyqrcode.create(ip)
        qr.png(QR_PATH, scale=12)
        feh_thread = Thread(target=feh)
        feh_thread.start()
        while True:
            try:
                with open(SETTINGS_PATH, 'r') as f:
                    settings = json.load(f)
            except json.decoder.JSONDecodeError:
                time.sleep(1)
            
            if settings['app_is_connected']:
                break
            else:
                time.sleep(1)
        
        os.system('killall feh')

    os.system(f'python3 {START_PATH}')


def getIP(remote_server="google.com"):
    """
    Return the/a network-facing IP number for this system.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: 
        s.connect((remote_server, 80))
        return s.getsockname()[0]

def feh():
    os.system(f'feh {QR_PATH} -F')

main()