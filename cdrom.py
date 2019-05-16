import os



class Cdrom():

    def __init__(self):
        pass
    def __del__(self):
        pass
    def open(self):
        os.system("/usr/bin/eject /dev/sr0 > /dev/null 2>&1 ")
    def close(self):
        os.system("/usr/bin/eject -t /dev/sr0 > /dev/null 2>&1 ")
