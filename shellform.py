from __future__ import unicode_literals
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window, FloatContainer, Float
from prompt_toolkit.layout.controls import FormattedTextControl, BufferControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.menus import CompletionsMenu


class ShellForm():
    def __init__(self, mainapp):
        self._main              = mainapp
        self._app               = self._main.application

        self._shell_completer    = WordCompleter([
                                    'alligator', 'ant', 'ape', 'bat', 'bear', 'beaver', 'bee', 'bison',
                                    'butterfly', 'cat', 'chicken', 'crocodile', 'dinosaur', 'dog', 'dolphin',
                                    'dove', 'duck', 'eagle', 'elephant', 'fish', 'goat', 'gorilla', 'kangaroo',
                                    'leopard', 'lion', 'mouse', 'rabbit', 'rat', 'snake', 'spider', 'turkey',
                                    'turtle',
                                ], ignore_case=True)


        self._kb                = KeyBindings()


        self._buffer            = Buffer( completer=self._shell_completer, complete_while_typing=True )

        self._container         = FloatContainer(content=HSplit([   Window(FormattedTextControl('Press "q" to quit.'), height=1, style='class:term.inv'),
                                                                    Window(BufferControl(buffer=self._buffer) , style='class:term') ] , key_bindings = self._kb),
                                                 floats=[Float(xcursor=True,ycursor=True,content=CompletionsMenu(max_height=16, scroll_offset=1))])

        self._layout            = Layout( container=self._container , focused_element=self._buffer )

        @self._kb.add('q')
        @self._kb.add('c-c')
        def _(event):
            " Quit application. "
            event.app.exit()
        @self._kb.add('c-e')
        def _(event):
            self._main.changeLayout('LOGIN')


    @property
    def layout(self):
        return self._layout

    def __del__(self):
        pass
