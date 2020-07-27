import json
import os
import time
from threading import Thread


class Feh_Manager:
    def __init__(self):
        self.__SETTINGS_PATH = os.path.abspath('settings.json')
        self.__PICS_PATH = os.path.abspath('pics')
    
    def run(self):
        with open(self.__SETTINGS_PATH, 'r') as f:
            settings = json.load(f)

        last_mode = settings['mode']
        last_photo = settings['display_photo']

        feh_thread = Thread(target=self.__restart_feh, args=(last_mode, last_photo))
        feh_thread.start()

        while True:
            try:
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
            except json.decoder.JSONDecodeError:
                time.sleep(1)
                continue

            mode = settings['mode']
            photo = settings['display_photo']

            if mode != last_mode:
                feh_thread = Thread(target=self.__restart_feh, args=(mode, photo))
                feh_thread.start()
            if mode == 'Single Photo' and photo != last_photo:
                feh_thread = Thread(target=self.__restart_feh, args=(mode, photo))
                feh_thread.start()
            
            last_mode = mode
            last_photo = photo
            time.sleep(1)

    def __restart_feh(self, mode, photo):
        if mode == 'Slideshow':
            os.system('killall feh')
            os.system(f'feh -Z -z -F -R 10 -D 3 --hide-pointer --auto-rotate {self.__PICS_PATH}')
        elif mode == 'Single Photo':
            with open('settings.json', 'r') as f:
                settings = json.load(f)
            photo = settings['display_photo']
            os.system('killall feh')
            path = os.path.join(self.__PICS_PATH, photo)
            os.system(f'feh {path} -F')
