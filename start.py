import multiprocessing
from threading import Thread

from feh_manager import Feh_Manager
from downloader import Downloader

def main():

    d = Downloader()
    fm = Feh_Manager()

    p1 = Thread(target=d.run())
    p2 = Thread(target=fm.run())
    p1.daemon = True
    p2.daemon = True
    p1.start()
    p2.start()

if __name__ == '__main__':
    main()