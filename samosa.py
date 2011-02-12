#This is the main file that will get called to start the service
from core.connection_set import ConnectionSet
from core.checker import Checker
from core.controller import Controller
from sys import argv, exit
from settings import CONNECTIONS, CHECK_INTERVAL, APPS

def connect():
    """Connect to backends."""
    conns = ConnectionSet()
    for cid, backend, kwargs in CONNECTIONS:
        c = __import__('backends.%s' %backend,globals(),locals(),['connection'],-1)
        conns.append(c.connection.Connection(cid,**kwargs))
    return conns
        
    
if __name__ == "__main__":

    if len(argv) > 1:
        alt_settings = __import__(argv[1],globals(),locals(),['CONNECTIONS', 'CHECK_INTERVAL', 'APPS'],-1)
        CONNECTIONS, CHECK_INTERVAL, APPS = alt_settings.CONNECTIONS, alt_settings.CHECK_INTERVAL, alt_settings.APPS    

    conns = connect()
#    msgs = conns.get_messages()
    controller = Controller(APPS)
    checker = Checker(controller,conns,CHECK_INTERVAL)
    checker.start()
    try:
        while True:
            todo = raw_input("\n\n**At any time enter c to force a check, q to quit.**\n\n")
            if todo == 'c':
                checker.check()
            elif todo == 'q':
                checker.stop()
                break
    except (KeyboardInterrupt, SystemExit):
        print "\n ** Recieved kill signal, stopping checker. **"
        checker.stop()
        exit(0) #kill the itty server thread too
        #raise
