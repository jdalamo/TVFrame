import json
import os
import time
from threading import Thread


def main():
    
    with open('settings.json', 'r') as f:
        settings = json.load(f)

    lastMode = settings['mode']
    lastPhoto = settings['display_photo']

    feh_thread = Thread(target=restart_feh, args=(lastMode, lastPhoto))
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

        if mode != lastMode:
            feh_thread = Thread(target=restart_feh, args=(mode, photo))
            feh_thread.start()
        elif photo != lastPhoto:
            feh_thread = Thread(target=restart_feh, args=(mode, photo))
            feh_thread.start()
        
        lastMode = mode
        lastPhoto = photo
        time.sleep(1)

def restart_feh(mode, photo):
    if mode == 'Slideshow':
        os.system('killall feh')
        os.system('feh -Z -z -R -F 10 -D 3 --hide-pointer --auto-rotate /home/pi/Desktop/slideshow/pics/')
    elif mode == "Single Photo":
        with open('settings.json', 'r') as f:
            settings = json.load(f)
        photo = settings['display_photo']
        os.system('killall feh')
        os.system(f'feh pics/{photo}')


if __name__ == '__main__':
    main()
