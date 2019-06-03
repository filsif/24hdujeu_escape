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
    def __init__(self,  shelloutput , shellprogress, cdrom, choice , comb ):
        threading.Thread.__init__(self)

        self.cdrom = cdrom
        self.shelloutput = shelloutput
        self.shellprogress = shellprogress
        self.comb = comb

        self.log_mon = [
        {"text" : "OK. I have all the components. Now melting." , "timeout" : 1},
        {"text" : "Melting" , "timeout" : 1},
        {"text" : "Melting" , "timeout" : 1},
        {"text" : "Melting (pfff )...", "timeout" : 1},
        {"text" : "Again Melting" , "timeout" : 5}

        ]

        self.run_choice = None
        self._nfc = None
        self._antidote = None

        if choice=="test_true":
            self.run_choice = self.run_test_true
        elif choice=="test_false":
            self.run_choice = self.run_test_false
        elif choice=="check":
            self.run_choice = self.run_check
        elif choice=="generate":
            self.run_choice = self.run_generate
    def run(self):
        self.run_choice()

    def run_test_true(self):
        self.run_test( "TRUE" )
    def run_test_false(self):
        self.run_test( "FALSE" )
    def run_generate(self):
        self.run_test(None)

    def nfc_init(self,type=None):
        self.shelloutput.nfc_lock = True

        if type is None:
            self._antidote = []
            self._nfc= NfcCardReader()


    def nfc_read(self,type=None):
        def progress( **kwargs):
            range = kwargs.get('range')
            msg = kwargs.get('msg')
            if range is not None:
                self.shellprogress.percentage = range
                if range == 100:
                    self.shelloutput.push("you can remove the component.")
                else:
                    self.shelloutput.flush()
            if msg is not None:
                self.shelloutput.push(msg)

        progress(range=0)
        if type is None:
            ret,id,label = self._nfc.parseBlock( progress )
            if ret == True:
                self._antidote.append(label)
                return True , label
            return False , None
        else:
            '''
            put progressb bar
            '''
            for i in range(1,100):
                progress(range=i)
                time.sleep(0.01)
            progress(range=100)
            return True , None

    def nfc_shut(self):
        self.shellprogress.percentage = 0
        self.shelloutput.nfc_lock = False

    def nfc_show_result(self,type):
        for elem in self.log_mon:
            self.shelloutput.push(elem['text'])
            time.sleep(elem['timeout'])

        if type is None:
            '''test antidote'''
            self.shelloutput.push("Congratulations... you was able to make the antidote !!!!")
            if self._antidote == self.comb:

                self.cdrom.open("TRUE")
            else:
                self.cdrom.open("FALSE")
        else:
            self.shelloutput.push("open cdrom " + type)
            self.cdrom.open(type)


    def run_check(self):
        self.nfc_init()

        self.shelloutput.push("Please put the element to check.")

        ret, label = self.nfc_read()
        if ret == True:
            self.shelloutput.push("the element is : " + label)
        else:
            self.shelloutput.push("No component detected or wrong detection.")

        self.nfc_shut()

    def run_test(self , type ):

        self.nfc_init(type)

        self.shelloutput.push("Welcome to the antidote tester.")
        test = True
        i = 0
        for elem in self.comb:
            i = i+1
            self.shelloutput.push("Please insert the element n° " + str(i))
            ret,_ = self.nfc_read(type)
            if ret == False:
                test = False
                self.shelloutput.push("No component detected... returning back to the shell")
                break

        if test == True:
            self.nfc_show_result(type)



        self.nfc_shut()




class ShellPrompt():
    def __init__(self , main ,header , output , progress ):
        self._main              = main
        self._superuser         = False

        self._cdrom             = Cdrom()

        self._login             = ""
        self._password          = "escape24"
        self._header            = header
        self._shelloutput       = output
        self._shellprogress     = progress
        self._combinaison       = ['element 1' , 'element 2' , 'element 3']
        self._commands          = [ 'grant' , 'help' ,'synthesis' , 'test' ,'check','clear' ,  'cdrom','quit']

        self._commands_help     = [ 'syntax is grant [user] [superuser|normal] [password]' ,
                                    'help lists all commands.\n help [command] show help for the command' ,
                                    'generate the antidote.Find the correct syntax',
                                    'allow you to test if the antidote is ok' ,
                                    'check an element',
                                    'clear the terminal, [history] the history, [all] both terminal and history',
                                    'syntax is cdrom [open|close] [TRUE|FALSE]',
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

        if buff.text.startswith("synthesis",0,len(buff.text)):
            self.do_synthesis(buff.text)
        else:
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
            if len(list) == 3:
                opt = list[1]
                type = list[2]

                if opt=="open":
                    self._cdrom.open(type)
                elif opt=="close":
                    self._cdrom.close(type)
        else:
            self._shelloutput.push("You are not allowed to use this command")

    def do_check(self,list):
        if self.su == True:
            a = monThread(self._shelloutput, self._shellprogress, self._cdrom ,"check" , self._combinaison)
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

    def do_synthesis(self,buffer):
        '''
        right syntax is :
        synthesis(x,t=1,ech=3,alt=nemesis,level=2)
        '''
        synthesis = { 'first' :'x' , 't' : '1' , 'ech' :'3' , 'alt' :'nemesis' , 'level' : '2' }

        allparms=['t','ech','alt','level']
        testparms=[]
        test=False
        try:
            b = buffer[9:]

            if b[0] == '(' and b[len(b)-1] ==')':
                b = b[1:-1]
                b_s = b.split(',')
                if b_s[0]=='x':
                    b_s=b_s[1:]
                    test=True
                    for elem in b_s:
                        sp = elem.split('=')
                        if synthesis[sp[0]] != sp[1]:
                            test = False
                        else:
                            testparms.append(sp[0])
                    if test==True:
                        if sorted(testparms)==sorted(allparms):
                            a = monThread(self._shelloutput, self._shellprogress, self._cdrom ,"generate" , self._combinaison )
                            a.start()
                            return
        except:
            pass
        self._shelloutput.push("Incorrect syntax. Please try again.")






    def do_test(self,list):
        if self.su == True:
            if len(list)==2:
                if list[1] == "TRUE":
                    test= "test_true"
                else:
                    test="test_false"
                a = monThread(self._shelloutput, self._shellprogress, self._cdrom ,test , self._combinaison)
                a.start()
        else:
            self._shelloutput.push("You are not allowed to use this command")

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
        self._buffer.document = Document( text = new_text , cursor_position = 0)

    def flush(self):
        new_text = datetime.datetime.now().strftime( '%H:%M:%S:%f') + self._buffer.text[15:]
        self._buffer.document = Document( text = new_text , cursor_position = 0)

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

        @self._kb.add('c-w')
        def _(event):
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
