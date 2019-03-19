import curses


class LoginForm():
    def __init__(self ,parentScreen):
        self.parentScreen = parentScreen


        parentHeight, parentWidth = parentScreen.getmaxyx()

        self.height = 10
        self.width = 50
        self.ypos = int( ( parentHeight - self.height ) / 2 )
        self.xpos = int( ( parentWidth - self.width ) / 2 )

        self.win = curses.newwin( self.height , self.width , self.ypos , self.xpos )
        self.win.keypad(1)
        self.win.attron(curses.color_pair(1))

        '''strings'''
        self.good_login     = 'frederic.mazur@gmail.com'
        self.good_password  = 'idefixx'
        self.strHeader      = ' Welcome Mr Unknown'
        self.strLogin       = 'User name :'
        self.strPassword    = 'Password  :'
        self.strError       = 'WRONG LOGIN OR PASSWORD'
        self.strError_safe  = '                       '

        ''' coordonnates'''
        self.LINE_ERROR     = 3
        self.LINE_LOGIN     = 5
        self.LINE_PASSWORD  = 6



        self.curLogin       = ''
        self.curPassword    = ''

        '''init box'''
        self.win.box()
        self.win.addstr(1 , int((self.width-len(self.strHeader)) /2) , self.strHeader, curses.color_pair(2) )
        self.win.addstr( self.LINE_LOGIN , 2, self.strLogin , curses.color_pair(1))
        self.win.addstr( self.LINE_PASSWORD , 2 , self.strPassword , curses.color_pair(1))
        self.win.move( self.LINE_LOGIN , 2 + len( self.strLogin) )

        y,x = self.win.getyx()
        self.rightX = x
        self.startX = x
        self.MAX_SIZE = 32

        self.error = False
        self.quit = False
        self.passwordOk = False

        curses.noecho()

    @property
    def valid(self):
        return self.passwordOk

    def __del__(self):
        curses.echo()

    def check_error(self):
        y,x = self.win.getyx()
        if self.error:
            self.win.attron(curses.A_BLINK)
            self.win.addstr( self.LINE_ERROR , 2, self.strError , curses.color_pair(1))
            self.win.attroff(curses.A_BLINK)
            self.error=False # reset after
        else:
            self.win.addstr( self.LINE_ERROR , 2, self.strError_safe , curses.color_pair(1))
        self.win.move(y,x)

    def do_break(self):
        self.quit = True
    def do_backspace(self):
        if self.rightX > self.startX:
            y , x = self.win.getyx()
            if y == self.LINE_LOGIN:
                self.curLogin = self.curLogin[:-1]
            elif y == self.LINE_PASSWORD:
                self.curPassword = self.curPassword[:-1]
            self.rightX -= 1
            self.win.addch(y,self.rightX,' ')
            self.win.move(y,self.rightX)

    def do_enter(self):
        y , x = self.win.getyx()
        if y == self.LINE_LOGIN:
            y = self.LINE_PASSWORD
            x = 2 + len(self.strPassword) + len(self.curPassword)
            self.rightX = x
            self.win.move(y,x)
        elif y == self.LINE_PASSWORD:
            '''validate password'''
            if self.curPassword==self.good_password and self.curLogin==self.good_login:
                self.quit = True
                self.passwordOk = True
            else:
                self.win.move( self.LINE_LOGIN, 2 + len(self.strLogin) )
                for _ in range(len(self.curLogin)):
                    self.win.addch(ord(' '))
                self.win.move( self.LINE_PASSWORD, 2 + len(self.strPassword) )
                for _ in range(len(self.curPassword)):
                    self.win.addch(ord(' '))
                self.curLogin=''
                self.curPassword=''
                self.rightX= self.startX
                self.error = True
                self.win.move( self.LINE_LOGIN, 2 + len(self.strLogin) )

    def do_move(self):
        y , x = self.win.getyx()
        if y == self.LINE_LOGIN:
            y = self.LINE_PASSWORD
            x = 2 + len(self.strPassword) + len(self.curPassword)
        elif y == self.LINE_PASSWORD:
            y = self.LINE_LOGIN
            x = 2 + len(self.strLogin) + len(self.curLogin)
        self.rightX = x
        self.win.move(y,x)

    def do_char(self,ch):
        curses.noraw()
        y , x = self.win.getyx()
        if x - self.startX < self.MAX_SIZE:
            if y == self.LINE_LOGIN:
                self.win.addch(ch)
                self.curLogin += chr(ch)
            elif y == self.LINE_PASSWORD:
                self.win.addch(ord('*'))
                self.curPassword += chr(ch)
            self.rightX +=1
            self.win.move(y , self.rightX)





    def getch(self):
        while not self.quit:
            curses.raw()
            self.check_error()
            ch = self.win.getch()
            if ch == 3: # CTRL-C
                self.do_break()
            elif ch == curses.KEY_BACKSPACE or ch == 8:
                '''
                BACKSPACE LINUX = 263 = KEY_BACKSPACE
                BACKSPACE WINDOWS = 8
                '''
                self.do_backspace()
            elif ch == curses.KEY_ENTER or ch == 459 or ch==13 or ch==10:
                '''
                ENTER LINUX = 343 = KEY_ENTER
                ENTER WINDOWS = 459
                RETURN LINUX = 10
                RETURN WINDOWS = 10
                '''
                self.do_enter()
            elif ch == curses.KEY_DOWN or ch == curses.KEY_UP:
                self.do_move()
            elif ch in range(65, 91) or \
                 ch in range(97, 123) or \
                 ch in range(49, 58) or \
                 ch == ord('@') or ch == ord('.'):
                 self.do_char(ch)
            self.win.refresh()


def main(stdscr):
    stdscr.clear()


    parentHeight, parentWidth = stdscr.getmaxyx() # Base window dimensions.


    curses.curs_set(1)
    curses.noraw()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)

    login_form = LoginForm(stdscr)

    login_form.getch()

    if login_form.valid:
        print("ok")



if __name__=='__main__':
    curses.wrapper(main)
