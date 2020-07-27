import json
import os
import png
import pyqrcode
import socket
import time
from threading import Thread

SETTINGS_PATH = os.path.abspath('settings.json')
MANAGER_PATH = os.path.abspath('manager.py')
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

    os.system(f'python3 {MANAGER_PATH}')


def getIP():
    return [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1][0]

def feh():
    os.system(f'feh {QR_PATH} -F')

main()