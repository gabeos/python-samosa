from time import sleep
from threading import Thread, Event
from random import randint
from datetime import datetime
import sys
import traceback

class Checker(Thread):
    """Checks messages and passes results to associated apps."""

    def __init__(self,controller,c_set,interval):
        Thread.__init__(self)
        self.event = Event()
        self.controller = controller
        self.connection_set = c_set
        self.interval = interval
        self.done = False

    def check(self):
        now = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")
        print "[%s] Checking %s" % (now,self.connection_set)
        self.controller.control(self.connection_set.get_messages())

    def run(self):
        while not self.done:
#            self.check()
            try:
                self.check()
            except Exception:
                print "Error: ", sys.exc_info()[0]
                traceback.print_exc()
                print "ignoring exception and continuing checker"
            #if interval is a tuple, take that as a range from which
            #to pick a random wait time
            if isinstance(self.interval,tuple):
                self.event.wait(randint(self.interval[0],self.interval[0]))
            else:
                self.event.wait(interval)

    def stop(self):
        self.done = True

