#This is the main file that will get called to start the service
from settings import *

def connect():
    """Connect to backend."""
    c = __import__('backends.pygooglevoice',globals(),locals(),['connection'],-1)
    dreload(c)
    dreload(c.connection.Connection)
    return c.connection.Connection()
    
if __name__ == "__main__":
    conn = connect()
    msgs = conn.get_messages()
