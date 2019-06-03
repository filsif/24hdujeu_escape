#!/usr/bin/env python
from __future__ import unicode_literals
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.layout import Layout, VSplit, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout.containers import  WindowAlign, HorizontalAlign,VerticalAlign
from prompt_toolkit.widgets import Frame
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.filters import Condition

from loginform import LoginForm
from shellform import ShellForm


class MainApp:
    def __init__(self):

        self.style              = Style([
                                ('terminal focused',    'bg:#aaaaaa'),
                                ('term',    '#00FF00'),
                                ('term.inv',    'bg:#00FF00 #000000'),
                                ('title', 'bg:#000044 #ffffff underline'),
                                ('progress-bar' , 'bg:#000000'),
                                ('progress-bar.used' , 'bg:#80FF80')
                                ])


        self.application        = Application(  layout=None,
                                        style=self.style,
                                        full_screen=True,
                                        mouse_support=True )

        self.loginform          = LoginForm( self )
        self.shellform          = ShellForm( self )

        self.application.layout = self.loginform.layout


        self.application.run()


    def __del__(self):
        pass

    def changeLayout(self,  type, **kwargs):
        if type == 'LOGIN':

            self.application.layout = self.loginform.layout
        elif type =='SHELL':
            if kwargs['login'] is not None:
                self.shellform.login = kwargs.get('login')
                self.application.layout = self.shellform.layout




if __name__ == '__main__':
    l = MainApp()
