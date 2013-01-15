#!/usr/bin/env python2

import sys
import multiprocessing
import time
import curses
try:
    import ping
except ImportError:
    print "ping module missing! You propably want to install it by typing 'pip install ping' in your terminal"
    sys.exit(1)


# Set Version
VERSION="0.1"

# Initialize ICMP DATA size to send
ICMP_DATA_SIZE=64

# Initialize main window margins
X_MARGIN = 5
Y_MARGIN = 5


def worker(queue,host,timeout=1):
    try:
        delay = (ping.do_one(host,timeout,ICMP_DATA_SIZE) or 0) * 1000
        queue.put((host,delay))
    except Exception:
        delay = 0
        queue.put(("%s not found"%host,delay))
    queue.close()


def do_ping(hostlist):
    jobs = []
    q = multiprocessing.Queue()
    for i in hostlist:
        p = multiprocessing.Process(target=worker,args=(q,i,))
        jobs.append(p)
        p.start()
    PROC_NUM=len(jobs)
    for j in jobs:
        j.join()
    out = []
    for i in range(PROC_NUM):
        out.append(q.get())
    return sorted(out)

def main(stdscr):
    myscreen = stdscr
    curses.start_color()
    
    # Initialize colors
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_YELLOW)

    # Get window sizes
    MAX_Y,MAX_X = myscreen.getmaxyx()

    # Init skeleton informations
    myscreen.border(0)
    myscreen.addstr(0, 10, "[ mping v %s ]"%(VERSION),curses.color_pair(1))
    myscreen.addstr(0, 30, "(press 'q' to exit)")

    # Headers
    myscreen.addstr(Y_MARGIN,X_MARGIN+15,"Hostname")
    myscreen.addstr(Y_MARGIN,X_MARGIN+28," | ")
    myscreen.addstr(Y_MARGIN,X_MARGIN+33," Time ")
    myscreen.addstr(Y_MARGIN+1,X_MARGIN+10,"+".rjust(20,"-"))
    myscreen.addstr(Y_MARGIN+1,X_MARGIN+30,"| 1000ms".rjust(MAX_X-45,"-"))

    myscreen.refresh()    
    
    # Read user input from args
    hostlist = sys.argv[1:]
        
    # Init new window to update
    view_pad = curses.newwin(50,MAX_X-2,Y_MARGIN+3,1)
    view_pad.nodelay(1)
    while True:
        if view_pad.getch() == ord('q'):
            break
        results = do_ping(hostlist)
        offset=0
        view_pad.erase()
        for host in results:
            delay = round(host[1],2)
            hostname = host[0][:30]
            bar_width = int(delay * MAX_X / 1000)
            color_pair = 2
            if delay > 200:
                color_pair = 4
                view_pad.addstr(1+offset, 0,"%30s"%(hostname),curses.color_pair(4))
            elif delay > 0 and delay < 200:
                color_pair = 2
                view_pad.addstr(1+offset, 0,"%30s"%(hostname))
            else:
                view_pad.addstr(1+offset, 0,"%30s"%(hostname),curses.color_pair(3))
                color_pair = 3

            view_pad.addstr(1+offset, X_MARGIN+30,"%*sms"%(bar_width,delay),curses.color_pair(color_pair))
            offset = offset + 2
        view_pad.vline(0,X_MARGIN+28,"|",len(results)*2+1)
        view_pad.refresh()
        time.sleep(1)
    curses.endwin()


if __name__ == "__main__":
    curses.wrapper(main) 
    
