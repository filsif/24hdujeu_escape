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


class LoginForm():
    def __init__(self, mainapp):
        self._is_err            = False
        self._valid             = False
        self._main              = mainapp
        self._app               = self._main.application
        self._login             = "test"
        self._password          = "test"
        self._text_intro        = Window( FormattedTextControl(HTML('please log in')) , width = 42 , height = 1  ,style="class:term.inv", align = WindowAlign.CENTER)


        self._text_ok           = Window( FormattedTextControl(HTML('Welcome Mr Unknown')) , width = 42 , height = 1  ,style="class:term.inv", align = WindowAlign.CENTER)


        self._text_error        = Window( FormattedTextControl(HTML('')) , width = 42 , height = 1  ,style="class:term", align = WindowAlign.CENTER)
        self._text_login        = TextArea( text='login    :' , width = 12 , height = 1  ,style="class:term")
        self._text_password     = TextArea( text='password :' , width = 12 , height = 1 ,style="class:term")
        self._text_curlogin     = TextArea(text='' ,multiline = False, width = 30 , height = 1,style="class:term" )
        self._text_curpassword  = TextArea(text='' , password = True , multiline = False, width = 30 , height = 1,style="class:term" )

        self._kb                = KeyBindings()

        self._container         = HSplit([
                                        VSplit([ self._text_intro  ],align = VerticalAlign.CENTER),
                                        VSplit([ self._text_error  ],align = VerticalAlign.CENTER),
                                        VSplit([ self._text_login,   self._text_curlogin  ],align = VerticalAlign.CENTER),
                                        VSplit([ self._text_password,   self._text_curpassword  ] ,align = VerticalAlign.CENTER),
                                ], align = HorizontalAlign.CENTER , key_bindings = self._kb)
        self._layout            = Layout( container=self._container,  focused_element=self._text_curlogin )




        @Condition
        def is_active():
            return self.is_err

        @self._kb.add( '<any>', filter=is_active)
        def _(event):
            self.is_err = False
            self._text_error.content.text = ""

        @self._kb.add('c-w')
        @self._kb.add('up')
        @self._kb.add('down')
        def _(event):
            self.switch_focus()

        @self._kb.add('enter')
        def _(event):
            self.validate_login()

        @self._kb.add('c-x', eager=True)
        def _(event):
            event.app.exit()

    def validate_login(self):
        if self._app.layout.has_focus(self._text_curlogin):
            self._app.layout.focus(self._text_curpassword)
        else:
            '''validate'''
            l = self._text_curlogin.text
            p = self._text_curpassword.text
            if l ==self._login and p ==self._password:
                self.valid = True
                self._main.changeLayout('SHELL')
            else:
                self._text_curlogin.text =''
                self._text_curpassword.text =''
                self.is_err = True
                self._text_error.content.text = "Wrong login or password"
                self._app.layout.focus(self._text_curlogin)


    def switch_focus(self):
        " Change focus when Control-W is pressed."

        if self._app.layout.has_focus(self._text_curlogin):
            self._app.layout.focus(self._text_curpassword)
        else:
            self._app.layout.focus(self._text_curlogin)



    @property
    def is_err(self):
        return self._is_err

    @is_err.setter
    def is_err(self, value ):
        self._is_err = value

    @property
    def valid(self):
        return self._valid

    @valid.setter
    def valid(self, value ):
        self._valid = value

    @property
    def layout(self):
        return self._layout

    def __del__(self):
        pass
