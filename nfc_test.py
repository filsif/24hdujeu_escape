from __future__ import print_function
from time import sleep

from smartcard.ReaderMonitoring import ReaderMonitor, ReaderObserver
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString


class printobserver(ReaderObserver):
    """A simple reader observer that is notified
    when readers are added/removed from the system and
    prints the list of readers
    """

    def update(self, observable, actions):
        (addedreaders, removedreaders) = actions
        print("Added readers", addedreaders)
        print("Removed readers", removedreaders)

# a simple card observer that prints inserted/removed cards
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

if __name__ == '__main__':
    print("Add or remove a smartcard reader to the system.")
    print("This program will exit in 10 seconds")
    print("")
    readermonitor = ReaderMonitor()
    readerobserver = printobserver()
    readermonitor.addObserver(readerobserver)

    cardmonitor = CardMonitor()
    cardobserver = PrintCardObserver()
    cardmonitor.addObserver(cardobserver)

    sleep(1000)

    # don't forget to remove observer, or the
    # monitor will poll forever...
    readermonitor.deleteObserver(readerobserver)
    cardmonitor.deleteObserver(cardobserver)
