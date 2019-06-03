from __future__ import print_function
from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.Exceptions import CardRequestTimeoutException
from bitstring import BitArray

import json
# define the apdus used in this script

import time


from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString


class apduCommands():
    def __init__(self):
        self._load_auth_key = [ 0xFF , 0x82 , 0x00 , 0x00 , 0x06 , 0xFF , 0xFF , 0xFF , 0xFF , 0xFF , 0xFF ]
        self._authenticate  = [ 0xFF , 0x86 , 0x00 , 0x00 , 0x05 , 0x01 , 0x00 , 0x00 , 0x61 , 0x00 ]
        self._read_binary   = [ 0xFF , 0xB0 , 0x00 , 0x00 , 0x00 ]

    def __del__(self):
        pass

    def loadAuthKey(self , key_num , key ):
        payload = self._load_auth_key
        if key_num == 0x00 or key_num == 0x01:
            payload[3] = key_num
        if key is not None and len(key)==6:
            payload = payload[:-6]
            payload += key
        return payload

    def authenticate( self , blk , key_type, key_num):
        payload = self._authenticate
        if blk >= 0x04 and blk <= 0x3F:
            payload[7] = blk
        if key_type=="typeA":
            payload[8] = 0x60
        elif key_type == "typeB":
            payload[8] = 0x61
        if key_num == 0x00 or key_num == 0x01:
            payload[9] = key_num
        return payload

    def readBinaryBlock(self, blk , nb):
        payload = self._read_binary
        if blk >= 0x04 and blk <= 0x3F:
            payload[3] = blk
        if nb >=0 and nb <= 0x10:
            payload[4] = nb
        return payload



class NfcCardReader():
    def __init__(self):
        self.apdu       = apduCommands()
        self.cardtype   = AnyCardType()
        self.key_id     = 0

    def __del__(self):
        pass

    def parseBlock(self, func):

        blk = []
        if self.readBlocks(10 , blk , func)== True:


            work = blk

            work = work[4:]

            ndef_header = BitArray(hex(work[0]))
            type_len = work[1]


            if ndef_header[0]==True and ndef_header[1]==True and ndef_header[2]==False:
                # bit 0 : Begin block
                # bit 1 : End block
                # bit 2 : Chunk Record
                # see : https://blog.zenika.com/2012/04/24/nfc-iv-les-types-de-messages-du-nfc-forum-wkt/
                if ndef_header[3]==True:
                    # bit 3 : short length
                    payload_len = work[2]
                    if ndef_header[4]==False:
                        # bit 4 : ID Field length present
                        if ndef_header[5:8]=="0b001":
                            # bit 5 - 6 - 7 : TNF bits
                            # 0b001 is WKT ( Well Known Type )
                            type = work[3]
                            if type==0x54:
                                # 0x54 == T = type texte
                                language_len = work[4]
                                payload = work[5:payload_len+4]

                                language = work[5:5+language_len]
                                real_payload = work[5+language_len:payload_len+4]
                                try:
                                    json_data = json.loads("".join(map(chr, real_payload)))

                                    if json_data['id'] and json_data['label']:
                                        return True, json_data['id'],json_data['label']

                                except:
                                    return False,None,None

                            else:
                                func (msg="No type T payload :" +hex(type))
                        else:
                            func(msg="No WKT payload")
                    else:
                        func(msg="ID Field length present.")
                else:
                    func(msg="no short len")
            else:
                func(msg="no single payload")
        else:
            func(msg="error in reading blocks")
        return False,None,None



    def readBlocks(self , to , totalBlk , func ):

        try:
            self.cardrequest = CardRequest(timeout=to, cardType=self.cardtype)
            self.cardservice = self.cardrequest.waitforcard()

            self.cardservice.connection.connect()

            if self.loadAuthKey() == True:

                for blk in range( 0x4 , 0x3F):
                    #retirer block keyA/access/keyB

                    if blk%4 != 3:

                        if self.authBlock( blk) == True:
                            curBlk = []
                            if self.readBlock( blk , curBlk) == True:

                                totalBlk+= curBlk

                                func( range=int(blk / 64 * 100))
                            else:
                                func(msg="failed to read block num " + str(blk))
                                self.cardservice.connection.disconnect()
                                return False
                        else:
                            func(msg="failed to auth block num "+ str(blk))
                            self.cardservice.connection.disconnect()
                            return False
                self.cardservice.connection.disconnect()


                func(range=100)
                cr = CardRequest()
                while True:
                    ce = cr.waitforcardevent()
                    func(msg="waitforcardevent")
                    time.sleep(0.3)
                    if len(ce)==0:
                        break



                return True
            else:
                func(msg="failed to load authkey")
                return False

        except CardRequestTimeoutException:
            func(msg="no card within 10 sec.")
            return False
    def loadAuthKey(self):
        try:
            payload = self.apdu.loadAuthKey( self.key_id,None )
            _, sw1, sw2 = self.cardservice.connection.transmit(payload)
            if sw1 == 0x90 and sw2 == 0x00:
                return True
        except:
            return False
        return False

    def authBlock(self, blk):
        try:

            payload = self.apdu.authenticate(blk , "typeB" , self.key_id )
            _, sw1, sw2 = self.cardservice.connection.transmit(payload)
            if sw1 == 0x90 and sw2 == 0x00:
                #print("auth block num [" + hex(blk) + "] ok")
                return True
            #print("ERROR auth block num ["+hex(blk) +"] "  + hex(sw1) + " " + hex(sw2) )
            return False
        except:
            return False
    def readBlock (self, blk, data):
        try:
            payload = self.apdu.readBinaryBlock(blk , 0x10 )
            d, sw1, sw2 = self.cardservice.connection.transmit(payload)
            if sw1 == 0x90 and sw2 == 0x00:
                #print("read block num [" + hex(blk) + "] ok")
                data+=d
                return True
            #print("ERROR read block num ["+hex(blk) +"] "  + hex(sw1) + " " + hex(sw2) )
            return False
        except:
            return False


class PrintCardObserver(CardObserver):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards
    """

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            print("+Inserted: ", toHexString(card.atr))
        for card in removedcards:
            print("-Removed: ", toHexString(card.atr))




if __name__ == "__main__":
    nfc= NfcCardReader()

    def func( **kwargs):
        msg = kwargs.get('msg')
        if msg is not None:
            print(msg)
        range = kwargs.get('range')
        if range is not None:
            print("range :"+str(range))

    ret,id,label = nfc.parseBlock(func)
    if ret == True:
        print("ok. Id : " + id + " label : " + label )
