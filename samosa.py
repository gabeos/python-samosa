#This is the main file that will get called to start the service
from settings import CONNECTIONS, CHECK_INTERVAL
from core import ConnectionSet, Checker

def connect():
    """Connect to backends."""
    conns = ConnectionSet()
    for cid, backend, kwargs in CONNECTIONS:
        c = __import__('backends.%s' %backend,globals(),locals(),['connection'],-1)
        conns.append(c.connection.Connection(cid,**kwargs))
    return conns
        
    
if __name__ == "__main__":
    conns = connect()
#    msgs = conns.get_messages()
    checker = Checker(conns,(12,22))
    checker.start()
    try:
        while True:
            todo = raw_input("Press c to check now, q to quit: ")
            if todo == 'c':
                checker.check()
            elif todo == 'q':
                checker.stop()
                break
    except (KeyboardInterrupt, SystemExit):
        print "\n ** Recieved kill signal, stopping checker. **"
        checker.stop()
        raise
