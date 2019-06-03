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
from prompt_toolkit.document import Document

import threading
from time import sleep


class loggedThread(threading.Thread):
    def __init__(self,form):
        threading.Thread.__init__(self)
        self._form = form
        self.log_connexion = []
        self.t=[
            { 'text' : 'try to determinate route...' , 'timeout' : 1 },
            { 'text' :'1    <1 ms    <1 ms     1 ms  10.4.30.1', 'timeout' : 0.1 },
            { 'text' :'2     1 ms    <1 ms    <1 ms  172.16.12.250', 'timeout' : 0.1 },
            { 'text' :'3     1 ms     1 ms     1 ms  192.168.1.1', 'timeout' : 0.1 },
            { 'text' :'4     4 ms     5 ms     5 ms  80.10.239.93', 'timeout' : 0.1 },
            { 'text' :'5    11 ms    19 ms    10 ms  ae119-0.ncorl102.Orleans.francetelecom.net [193.251.108.118]', 'timeout' : 1.5 },
            { 'text' :'6    25 ms    12 ms    10 ms  ae42-0.niidf102.Aubervilliers.francetelecom.net [193.252.159.62]', 'timeout' : 1.5 },
            { 'text' :'7    14 ms     9 ms    11 ms  ae40-0.niidf101.Paris3eArrondissement.francetelecom.net [81.253.129.137]', 'timeout' : 0.1 },
            { 'text' :'8    16 ms    16 ms    19 ms  193.252.137.10', 'timeout' : 0.1 },
            { 'text' :'9    10 ms    10 ms    10 ms  74.125.50.250', 'timeout' : 0.1 },
            { 'text' :'10    10 ms    11 ms    10 ms  108.170.244.161', 'timeout' : 0.1 },
            { 'text' :'11    10 ms    10 ms    10 ms  216.239.48.27', 'timeout' : 1 },
            { 'text' :'12    11 ms    10 ms    10 ms  par10s33-in-f3.1e100.net [216.58.201.227]', 'timeout' : 1 },
            { 'text' :'Generating public/private rsa key pair.', 'timeout' : 3 },
            { 'text' :'Your identification has been saved in /etc/ssh/private/key.priv.', 'timeout' : 0.1 },
            { 'text' :'Your public key has been saved in /etc/ssh/public/key.pub.', 'timeout' : 0.1 },
            { 'text' :'The key fingerprint is:', 'timeout' : 0.1 },
            { 'text' :'28:aa:e1:5e:d3:c2:c8:14:1a:b3:b8:8f:95:8e:ad:12 root@sd-102108', 'timeout' : 0.1 },
            { 'text' :'The key\'s randomart image is:', 'timeout' : 1 },
            { 'text' :'+---[RSA 2048]----+', 'timeout' : 0.1 },
            { 'text' :'|                 |', 'timeout' : 0.1 },
            { 'text' :'|                 |', 'timeout' : 0.1 },
            { 'text' :'|o.               |', 'timeout' : 0.1 },
            { 'text' :'|o+.    .         |', 'timeout' : 0.1 },
            { 'text' :'|+.  . . S        |', 'timeout' : 0.1 },
            { 'text' :'|E.oo..           |', 'timeout' : 0.1 },
            { 'text' :'|o++= .           |', 'timeout' : 0.1 },
            { 'text' :'|oX. o            |', 'timeout' : 0.1 },
            { 'text' :'|B++              |', 'timeout' : 0.1 },
            { 'text' :'+-----------------+', 'timeout' : 0.1 },
            { 'text' : 'Connecting to a23-217-231-118.deploy.static.akamaitechnologies.com:8868 ...' , 'timeout' : 3 },
            { 'text' : 'Connected !!!' , 'timeout' : 1 },

        ]

    def __del__(self):
        pass

    def push(self,text,d):
        a = self._form._text_logged
        newtext = a.text + '\n'+text
        a.buffer.document = Document(text = newtext , cursor_position=len(newtext))
        sleep(d)
    def clean(self):
        self._form.valid = True
        self._form._app.layout.focus(self._form._text_curlogin)
        self._form._text_curlogin.text =""
        self._form._text_curpassword.text=""
        self._form._text_logged.text = ''

    def login(self):
        self._form._app.layout.focus(self._form._text_logged)
        for e in self.log_connexion:
            self.push(e['text'] , e['timeout'])




    def run(self):

        '''
        add text login
        '''
        self.login()
        self.clean()
        self._form._main.changeLayout('SHELL' , login=self._form._login )






class LoginForm():
    def __init__(self, mainapp):
        self._is_err            = False
        self._valid             = False
        self._main              = mainapp
        self._app               = self._main.application
        self._login             = "hercule"
        self._password          = "virus"
        self._text_intro        = Window( FormattedTextControl(HTML('please log in')) , width = 42 , height = 1  ,style="class:term.inv", align = WindowAlign.CENTER)


        self._text_ok           = Window( FormattedTextControl(HTML('Welcome Mr Unknown')) , width = 42 , height = 1  ,style="class:term.inv", align = WindowAlign.CENTER)


        self._text_error        = Window( FormattedTextControl(HTML('')) , width = 42 , height = 1  ,style="class:term", align = WindowAlign.CENTER)
        self._text_login        = TextArea( text='login    :' , width = 12 , height = 1  ,style="class:term")
        self._text_password     = TextArea( text='password :' , width = 12 , height = 1 ,style="class:term")
        self._text_curlogin     = TextArea(text='' ,multiline = False, width = 30 , height = 1,style="class:term" )
        self._text_curpassword  = TextArea(text='' , password = True , multiline = False, width = 30 , height = 1,style="class:term" )
        self._text_logged       = TextArea(text='' ,multiline = True, width = 120 , height = 20,style="class:term" )

        self._kb                = KeyBindings()

        self._container         = HSplit([
                                        VSplit([ self._text_intro  ],align = VerticalAlign.CENTER),
                                        VSplit([ self._text_error  ],align = VerticalAlign.CENTER),
                                        VSplit([ self._text_login,   self._text_curlogin  ],align = VerticalAlign.CENTER),
                                        VSplit([ self._text_password,   self._text_curpassword  ] ,align = VerticalAlign.CENTER),
                                        VSplit([ self._text_logged ] ,align = VerticalAlign.CENTER),
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
                a = loggedThread(self)
                a.start()
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
