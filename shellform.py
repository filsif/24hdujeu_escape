from __future__ import unicode_literals
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer

from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window, FloatContainer, Float
from prompt_toolkit.layout.controls import FormattedTextControl, BufferControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.layout.processors import BeforeInput,ShowArg
from prompt_toolkit.document import Document
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.filters import Condition
from prompt_toolkit.widgets import ProgressBar
from prompt_toolkit.styles import Style

from cdrom import Cdrom

import datetime
import threading
import time
import os

from nfc import NfcCardReader


class monThread(threading.Thread):
    def __init__(self,  shelloutput , shellprogress, cdrom, choice):
        threading.Thread.__init__(self)

        self.cdrom = cdrom
        self.shelloutput = shelloutput
        self.shellprogress = shellprogress

        self.run_choice = None

        if choice=="test":
            self.run_choice = self.run_test
        elif choice=="check":
            self.run_choice = self.run_check
    def run(self):
        self.run_choice()

    def run_check(self):
        self.shelloutput.nfc_lock = True

        self.shelloutput.push("Please put the element to check.")

        nfc= NfcCardReader()

        def progress( range):
            self.shellprogress.percentage = range
            if range == 100:
                self.shelloutput.push("you can remove the component.")
            else:
                self.shelloutput.flush()

        self.shellprogress.percentage = 0
        ret,id,label = nfc.parseBlock( progress )
        if ret == True:
            self.shelloutput.push("the element is : " + label)
        else:
            self.shelloutput.push("No component detected or wrong detection.")

        self.shellprogress.percentage = 0
        self.shelloutput.nfc_lock = False


    def run_test(self):
        self.shelloutput.nfc_lock = True



        self.shelloutput.push("Welcome to the antidote tester.")

        self.shelloutput.push("Please insert the first element.")


        antidote = []
        nfc= NfcCardReader()

        def progress( range):
            self.shellprogress.percentage = range
            if range == 100:
                self.shelloutput.push("you can remove the component.")
            else:
                self.shelloutput.flush()

        self.shellprogress.percentage = 0
        ret,id,label = nfc.parseBlock( progress )
        if ret == True:
            antidote.append(label)
            self.shelloutput.push("OK. Please insert the second element.")


            self.shellprogress.percentage = 0
            ret,id,label = nfc.parseBlock( progress )
            if ret==True:
                antidote.append(label)
                self.shelloutput.push("OK. Please insert the third element.")

                self.shellprogress.percentage = 0
                ret,id,label = nfc.parseBlock( progress )
                if ret == True:
                    antidote.append(label)
                    self.shelloutput.push("OK. Please insert the fourth element.")

                    self.shellprogress.percentage = 0
                    ret,id,label = nfc.parseBlock( progress )
                    if ret==True:
                        antidote.append(label)
                        self.shelloutput.push("OK. I have the four components. Now melting.")
                        time.sleep(1)
                        self.shelloutput.push("Melting...")
                        time.sleep(1)
                        self.shelloutput.push("Melting...")
                        time.sleep(1)
                        self.shelloutput.push("Melting...")
                        time.sleep(1)
                        self.shelloutput.push("Melting ( pfff )...")
                        time.sleep(1)
                        self.shelloutput.push("again Melting...")
                        time.sleep(5)
                        a = str(antidote)

                        if antidote[0]=='element 1' and antidote[1] =='element 2' and antidote[2] == 'element 3' and antidote[3]=='element 4':
                            self.shelloutput.push("Congratulations... you was able to make the antidote !!!!")
                            self.cdrom.open()
                        else:
                            self.shelloutput.push("Sorry, please try later")


                    else:
                        self.shelloutput.push("No component detected... returning back to the shell.")


                else:
                    self.shelloutput.push("No component detected... returning back to the shell.")


            else:
                self.shelloutput.push("No component detected... returning back to the shell.")


        else:
            self.shelloutput.push("No component detected... returning back to the shell")



        self.shellprogress.percentage = 0
        self.shelloutput.nfc_lock = False



class ShellPrompt():
    def __init__(self , main ,header , output , progress ):
        self._main              = main
        self._superuser         = False

        self._cdrom             = Cdrom()

        self._login             = ""
        self._password          = "psyCZJNG"
        self._header            = header
        self._shelloutput       = output
        self._shellprogress     = progress
        self._commands          = [ 'grant' , 'help' ,'test' ,'check','clear' ,  'cdrom','quit']

        self._commands_help     = [ 'syntax is grant [user] [superuser|normal] [password]' ,
                                    'help lists all commands.\n help [command] show help for the command' ,
                                    'allow you to test if the antidote is ok' ,
                                    'check an element'
                                    'clear the terminal, [history] the history, [all] both terminal and history',
                                    'syntax is cdrom [open|close]',
                                    'return to login prompt']

        self._shell_completer   = WordCompleter( self._commands , ignore_case=True)

        self._buffer            = Buffer( multiline=False , accept_handler = self.accept , auto_suggest = AutoSuggestFromHistory() , enable_history_search=True , completer=self._shell_completer)
        self._buffercontrol     = BufferControl(buffer=self._buffer ,input_processors=[ BeforeInput('root@prof:/home/prof# ') ] )
        self._window            = Window( self._buffercontrol , style='class:term' , height=1)

    @property
    def login(self):
        return self._login
    @login.setter
    def login(self,value):
        self._login = value

    @property
    def pw(self):
        return self._password
    @pw.setter
    def pw(self,value):
        self._password = value

    @property
    def su(self):
        return self._superuser

    @su.setter
    def su(self,value):
        self._superuser = value


    def accept(self ,buff):
        buf_split = buff.text.split()

        if len(buf_split)>0:
            if buf_split[0] in self._commands:
                getattr(self, "do_" + buf_split[0])(buf_split)
            else:
                self.do_unknown(buff.text)


    def do_grant(self,list):
        if len(list) == 4:
            if list[1] == self.login and list[3] == self.pw:
                if list[2] =="superuser":
                    self._header.text = 'Press "ctrl-c" to quit. * superuser *'
                    self.su = True
                elif list[2]== "normal":
                    self._header.text = 'Press "ctrl-c" to quit.'
                    self.su = False
                else:
                    self._shelloutput.push("syntax is grant [user] [superuser|normal] [password]")
            else:
                self._shelloutput.push("syntax is grant [user] [superuser|normal] [password]")
        else:
            self._shelloutput.push("syntax is grant [user] [superuser|normal] [password]")


    def do_cdrom(self,list):
        if self.su == True:
            if len(list) == 2:
                opt = list[1]

                if opt=="open":
                    self._cdrom.open()
                elif opt=="close":
                    self._cdrom.close()
        else:
            self._shelloutput.push("You are not allowed to use this command")

    def do_check(self,list):
        if self.su == True:
            a = monThread(self._shelloutput, self._shellprogress, self._cdrom ,"check")
            a.start()

        else:
            self._shelloutput.push("You are not allowed to use this command")


    def do_help(self,list):
        if len(list) == 1:
            string = "commands are : "
            for elem in self._commands:
                string += "["+elem + "] "
            self._shelloutput.push(string )
        elif len(list) == 2:
            if list[1] in self._commands:
                idx = self._commands.index(list[1])
                self._shelloutput.push(self._commands_help[idx] )


    def do_test(self,list):

        a = monThread(self._shelloutput, self._shellprogress, self._cdrom ,"test")
        a.start()

    def do_clear(self,list):
        if len(list)==1:
            self._shelloutput.clear()
        elif len(list)==2:
            if list[1]=='term':
                self._shelloutput.clear()
            elif list[1]=='history':
                self._shelloutput._buffer.history = InMemoryHistory()
                pass
            elif list[1]=='all':
                self._shelloutput._buffer.history = InMemoryHistory()
                self._shelloutput.clear()

        else:
            self._shelloutput.push('syntax is :clear [term|history|all]')


    def do_unknown(self,txt):
        self._shelloutput.push("unknown command ["+txt+"]")

    def do_quit(self,list):
        self.su = False
        self._header.text = 'Press "ctrl-c" to quit.'
        self._shelloutput.clear()
        self._main.changeLayout('LOGIN' )

    @property
    def window(self):
        return self._window


class ShellOutput():
    def __init__(self):
        self._buffer = Buffer( multiline=True )
        self._buffercontrol = BufferControl(buffer=self._buffer )
        self._window = Window( self._buffercontrol , style='class:term' )
        self.nfc_lock = False

    @property
    def window(self):
        return self._window

    def push(self, text):
        string = datetime.datetime.now().strftime( '%H:%M:%S:%f')
        new_text =  string + ' - ' + text+'\n' +self._buffer.text
        self._buffer.document = Document( text = new_text , cursor_position = len(new_text))

    def flush(self):
        new_text = datetime.datetime.now().strftime( '%H:%M:%S:%f') + self._buffer.text[15:]
        self._buffer.document = Document( text = new_text , cursor_position = len(new_text))

    def clear(self):
        self._buffer.reset()



class ShellForm():
    def __init__(self, mainapp):
        self._main              = mainapp
        self._app               = self._main.application


        self._kb                = KeyBindings()
        self._header            = FormattedTextControl('Press "ctrl-c" to quit.')
        self._shelloutput       = ShellOutput()
        self._shellprogress     = ProgressBar()
        self._shellprompt       = ShellPrompt(self._main ,self._header  , self._shelloutput , self._shellprogress )
        self._shellprogress.percentage = 0



        self._container         = FloatContainer(content= HSplit([ Window(self._header, height=1, style='class:term.inv'),
                                                                   self._shellprogress,
                                                                   self._shellprompt.window,
                                                                   self._shelloutput.window ] ,key_bindings = self._kb ),
                                                 floats=[Float(xcursor=True,ycursor=True,content=CompletionsMenu(max_height=16, scroll_offset=1))])

        self._layout            = Layout( container=self._container  , focused_element= self._shellprompt.window )




        @Condition
        def is_active():
            return self._shelloutput.nfc_lock

        @Condition
        def is_su():
            return self._shellprompt.su

        @self._kb.add( '<any>', filter=is_active)
        def _(event):
            pass

        @self._kb.add('c-c', filter=is_su)
        def _(event):
            " Quit application. "
            event.app.exit()




    @property
    def login(self):
        return self._shellprompt.login
    @login.setter
    def login(self,value):
        self._shellprompt.login = value


    @property
    def layout(self):
        return self._layout

    def __del__(self):
        pass
