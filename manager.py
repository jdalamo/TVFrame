import concurrent.futures
from feh_manager import Feh_Manager
from downloader import Downloader

d = Downloader()
fm = Feh_Manager()

with concurrent.futures.ProcessPoolExecutor() as executor:
    f1 = executor.submit(d.run())
    f2 = executor.submit(fm.run())