import os



class Cdrom():

    def __init__(self):
        self.cdrom_true_name = "HL-DT-ST"
        self.cdrom_false_name = "ASUS"
        self.cmd = "dmesg | grep  `dmesg | grep %s | awk '{print $4}' |tail -1` | grep 'Attached scsi CD-ROM' | awk '{print $8}' |tail -1"

        res = os.popen(self.cmd %self.cdrom_true_name).readlines()

        self.cdrom_true = None

        if len(res)==1:
            self.cdrom_true = '/dev/' + res[0]
            self.cdrom_true = self.cdrom_true[:-1]

        res = os.popen(self.cmd %self.cdrom_false_name).readlines()


        self.cdrom_false = None
        if len(res)==1:
            self.cdrom_false = '/dev/' + res[0]
            self.cdrom_false = self.cdrom_false[:-1]
        #self.cdrom_true     = '/dev/sr0'
        #self.cdrom_false    = '/dev/sr1'





    def __del__(self):
        pass
    def open(self, type):
        if type=="TRUE":
            if self.cdrom_true is not None:
                os.system("/usr/bin/eject %s > /dev/null 2>&1 " % self.cdrom_true)
        elif type=="FALSE":
            if self.cdrom_false is not None:
                os.system("/usr/bin/eject %s > /dev/null 2>&1 " % self.cdrom_false)
    def close(self, type):
        if type=="TRUE":
            if self.cdrom_true is not None:
                os.system("/usr/bin/eject -t %s > /dev/null 2>&1 " % self.cdrom_true)
        elif type=="FALSE":
            if self.cdrom_false is not None:
                os.system("/usr/bin/eject -t %s > /dev/null 2>&1 " % self.cdrom_false)


if __name__ =="__main__":
    cdrom = Cdrom()
