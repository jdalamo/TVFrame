from threading import Thread

from feh_manager import Feh_Manager
from downloader import Downloader

if __name__ == '__main__':

    d = Downloader()
    fm = Feh_Manager()

    p1 = Thread(target=d.run())
    p2 = Thread(target=fm.run())

    p1.start()
    p2.start()