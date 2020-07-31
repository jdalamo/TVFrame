import json
import os
import random
import time
from threading import Thread


class Feh_Manager:
    def __init__(self):
        self.__SETTINGS_PATH = os.path.abspath('settings.json')
        self.__PICS_PATH = os.path.abspath('pics')
        self.__DEFAULT_IMAGE_PATH = os.path.abspath('default.jpg')
    
    def run(self):
        try:
            last_mode, last_photo, pics = self.__update()
        except json.decoder.JSONDecodeError:
            last_mode = 'Slideshow'
            pics = [p for p in os.listdir(self.__PICS_PATH) if os.path.isfile(os.path.join(self.__PICS_PATH, p)) and p != '.DS_Store']
            if pics:
                last_photo = random.choice(pics)
            else:
                last_photo = self.__DEFAULT_IMAGE_PATH
        
        if pics:
            feh_thread = Thread(target=self.__restart_feh, args=(last_mode, last_photo))
        else:
            feh_thread = Thread(target=self.__show_default)
        feh_thread.start()

        while True:
            try:
                mode, photo, pics = self.__update()
            except json.decoder.JSONDecodeError:
                time.sleep(1)
                continue
            
            if pics:
                if mode != last_mode:
                    feh_thread = Thread(target=self.__restart_feh, args=(mode, photo))
                    feh_thread.start()
                if mode == 'Single Photo' and photo != last_photo:
                    if photo == "":
                        feh_thread = Thread(target=self.__restart_feh, args=(mode, random.choice(pics)))
                    else:
                        feh_thread = Thread(target=self.__restart_feh, args=(mode, photo))
                    feh_thread.start()
            else:
                if last_mode == 'Default':
                    continue
                feh_thread = Thread(target=self.__show_default)
                feh_thread.start()
                mode = 'Default'
            
            last_mode = mode
            last_photo = photo
            time.sleep(1)

    def __update(self):
        with open(self.__SETTINGS_PATH, 'r') as f:
            settings = json.load(f)
        pics = [p for p in os.listdir(self.__PICS_PATH) if os.path.isfile(os.path.join(self.__PICS_PATH, p)) and p != '.DS_Store']

        mode = settings['mode']
        photo = settings['display_photo']

        return (mode, photo, pics)

    def __show_default(self):
        os.system('killall feh')
        os.system(f'feh {self.__DEFAULT_IMAGE_PATH} -F --hide-pointer --auto-rotate')

    def __restart_feh(self, mode, photo):
        print(self.__PICS_PATH)
        if mode == 'Slideshow':
            os.system('killall feh')
            os.system(f'feh -Z -z -F -R 10 -D 3 --hide-pointer --auto-rotate {self.__PICS_PATH}')
        elif mode == 'Single Photo':
            with open('settings.json', 'r') as f:
                settings = json.load(f)
            photo = settings['display_photo']
            os.system('killall feh')
            path = os.path.join(self.__PICS_PATH, photo)
            os.system(f'feh {path} -F --hide-pointer --auto-rotate')
