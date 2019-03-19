import curses

def main(stdscr):
    stdscr.clear()



    parentHeight, parentWidth = stdscr.getmaxyx() # Base window dimensions.


    curses.curs_set(1)
    curses.noraw()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)


    good_login="frederic.mazur@gmail.com"
    good_password="idefixx"

    height = 10
    width = 50
    ypos = int((parentHeight - height) / 2)
    xpos = int((parentWidth - width) / 2)
    win = curses.newwin(height, width, ypos, xpos)
    win.attron(curses.color_pair(1))

    win.keypad(1)
    strHeader =   ' Welcome Mr Unknown'
    strLogin =    'User name :'
    strPassword = 'Password  :'

    strError = 'WRONG LOGIN OR PASSWORD'
    strError_safe = '                       '


    LINE_ERROR = 3
    LINE_LOGIN = 5
    LINE_PASSWORD = 6
    win.box()



    password = ''
    login = ''

    win.addstr(1, int((width-len(strHeader)) /2)  , strHeader,   curses.color_pair(2) )
    win.addstr( LINE_LOGIN      , 2, strLogin   , curses.color_pair(1))
    win.addstr( LINE_PASSWORD   , 2, strPassword, curses.color_pair(1))
    win.move( LINE_LOGIN , 2 + len(strLogin) )

    y,x = win.getyx()
    rightX = x
    START_POS = x
    MAX_SIZE= 32

    error = False
    quitting = False
    curses.noecho()
    while not quitting:
        curses.raw()

        y,x = win.getyx()
        if error:
            win.attron(curses.A_ITALIC)
            win.addstr( LINE_ERROR      , 2, strError   , curses.color_pair(1))
            win.attroff(curses.A_ITALIC)
            error=False # reset after
        else:
            win.addstr( LINE_ERROR      , 2, strError_safe   , curses.color_pair(1))
        win.move(y,x)


        ch = win.getch()
        if ch ==3: # CTRL-C
            quitting = True
        elif ch == curses.KEY_BACKSPACE or ch == 8:
            '''
            BACKSPACE LINUX = 263 = KEY_BACKSPACE
            BACKSPACE WINDOWS = 8
            '''

            if rightX > START_POS:
                y , x = win.getyx()
                if y == LINE_LOGIN:
                    login = login[:-1]
                elif y == LINE_PASSWORD:
                    password = password[:-1]
                rightX -= 1

                win.addch(y,rightX,' ')
                win.move(y,rightX)
        elif ch == curses.KEY_ENTER or ch == 459 or ch==13:
            '''
            ENTER LINUX = 343 = KEY_ENTER
            ENTER WINDOWS = 459
            RETURN LINUX = 10
            RETURN WINDOWS = 10
            '''
            y , x = win.getyx()
            if y == LINE_LOGIN:
                y = LINE_PASSWORD
                x = 2 + len(strPassword) + len(password)
                rightX = x
                win.move(y,x)
            elif y == LINE_PASSWORD:
                '''validate password'''
                if password==good_password and login==good_login:
                    quitting = True
                else:
                    win.move( LINE_LOGIN, 2 + len(strLogin) )
                    for _ in range(len(login)):
                        win.addch(ord(' '))
                    win.move( LINE_PASSWORD, 2 + len(strPassword) )
                    for _ in range(len(password)):
                        win.addch(ord(' '))
                    login=''
                    password=''
                    rightX= START_POS
                    error = True
                    win.move( LINE_LOGIN, 2 + len(strLogin) )
        elif ch == curses.KEY_DOWN or ch == curses.KEY_UP:
            y , x = win.getyx()
            if y == LINE_LOGIN:
                y = LINE_PASSWORD
                x = 2 + len(strPassword) + len(password)
            elif y == LINE_PASSWORD:
                y = LINE_LOGIN
                x = 2 + len(strLogin) + len(login)
            rightX = x
            win.move(y,x)
        elif ch in range(65, 91) or \
             ch in range(97, 123) or \
             ch in range(49, 58) or \
             ch == ord('@') or ch == ord('.'):
            curses.noraw()
            y , x = win.getyx()
            if x - START_POS < MAX_SIZE:
                if y == LINE_LOGIN:
                    win.addch(ch)
                    login += chr(ch)
                elif y == LINE_PASSWORD:
                    win.addch(ord('�'))
                    password += chr(ch)
                rightX +=1
                win.move(y , rightX)
        win.refresh()

if __name__=='__main__':
    curses.wrapper(main)
