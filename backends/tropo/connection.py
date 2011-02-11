import backends.tropo.util
from core.message_set import MessageSet
from core.connection import Connection as SuperConn

class Connection(SuperConn):
    """stores received messages in MongoDB"""

    def get_messages(self):
        """Retrieves messages from MongoDB"""
        return self.listener.get_new_messages()

    def send(self,msg):
        """Mimic sending a message
        Send a message to a different MongoDB specified by phone number in msg
        Also creates outgoing message in sender MongoDB"""

        pass

def __init__(self,cid,**args):
    """Connection to single MongoDB
    kwargs:
        NUMBER = phoneish number
        reference to db #TODO"""


    self.id = cid

    self.num = args['NUMBER']
    self.backend = 'tropo'


