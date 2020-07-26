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
        if mode == 'Single Photo' and photo != lastPhoto:
            feh_thread = Thread(target=restart_feh, args=(mode, photo))
            feh_thread.start()
        
        lastMode = mode
        lastPhoto = photo
        time.sleep(1)

def restart_feh(mode, photo):
    pics_path = os.path.abspath('pics')
    if mode == 'Slideshow':
        os.system('killall feh')
        os.system(f'feh -Z -z -F -R 10 -D 3 --hide-pointer --auto-rotate {pics_path}')
    elif mode == 'Single Photo':
        with open('settings.json', 'r') as f:
            settings = json.load(f)
        photo = settings['display_photo']
        os.system('killall feh')
        path = os.path.join(pics_path, photo)
        os.system(f'feh {path} -F')


if __name__ == '__main__':
    main()
