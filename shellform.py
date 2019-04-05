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

import datetime



class ShellPrompt():
    def __init__(self , output):
        self._shelloutput = output
        self._commands = [ 'grant' , 'help' ,'test' ,'clear' ,'quit']

        self._commands_help = [ 'syntax is grant [user] [superuser|normal]' ,
                                'help lists all commands.\n help [command] show help for the command' ,
                                'allow you to test if the antidote is ok' ,
                                'clear the terminal']

        self._shell_completer    = WordCompleter( self._commands , ignore_case=True)

        self._buffer = Buffer( multiline=False , accept_handler = self.accept , auto_suggest = AutoSuggestFromHistory() , enable_history_search=True , completer=self._shell_completer)
        self._buffercontrol = BufferControl(buffer=self._buffer ,input_processors=[ BeforeInput('root@prof:/home/prof# ') ] )
        self._window = Window( self._buffercontrol , style='class:term' , height=1)

    def accept(self ,buff):
        buf_split = buff.text.split()

        if len(buf_split)>0:
            if buf_split[0] in self._commands:
                getattr(self, "do_" + buf_split[0])(buf_split)
            else:
                self.do_unknown(buff.text)


    def do_grant(self,list):
        pass

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
        pass
    def do_clear(self,list):
        self._shelloutput.clear()

    def do_unknown(self,txt):
        self._shelloutput.push("unknown command ["+txt+"]")

    def do_quit(self,list):
        pass

    @property
    def window(self):
        return self._window


class ShellOutput():
    def __init__(self):
        self._buffer = Buffer( multiline=True )
        self._buffercontrol = BufferControl(buffer=self._buffer )
        self._window = Window( self._buffercontrol , style='class:term' )

    @property
    def window(self):
        return self._window

    def push(self, text):


        string = datetime.datetime.now().strftime( '%H:%M:%S:%f')
        new_text =  string + ' - ' + text+'\n' +self._buffer.text
        self._buffer.document = Document( text = new_text , cursor_position = len(new_text))

    def clear(self):
        new_text = ""
        self._buffer.document = Document( text = new_text , cursor_position = len(new_text))


class ShellForm():
    def __init__(self, mainapp):
        self._main              = mainapp
        self._app               = self._main.application

        self._kb                = KeyBindings()
        self._shelloutput       = ShellOutput()
        self._shellprompt       = ShellPrompt(self._shelloutput )


        self._container         = FloatContainer(content= HSplit([ Window(FormattedTextControl('Press "ctrl-c" to quit.'), height=1, style='class:term.inv'),
                                                                   self._shellprompt.window,
                                                                   self._shelloutput.window ] ,key_bindings = self._kb ),
                                                 floats=[Float(xcursor=True,ycursor=True,content=CompletionsMenu(max_height=16, scroll_offset=1))])

        self._layout            = Layout( container=self._container  , focused_element= self._shellprompt.window )




        @self._kb.add('c-c')
        def _(event):
            " Quit application. "
            event.app.exit()







    @property
    def layout(self):
        return self._layout

    def __del__(self):
        pass
