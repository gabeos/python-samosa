import backends.commandloop.util
from core.message_set import MessageSet
from core.connection import Connection as SuperConn
import mongoengine as ME


class Connection(SuperConn):
    """Manages connections with user modifiable MongoDB"""

    def get_messages(self):
        """Retrieves messages from MongoDB"""

        return 

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

    print "Connecting to MongoDB that mimics phone # " % args['NUMBER']
    
    self.db = ME.connect('virtualbackend')
    self.vphone = VirtualPhone(number=args['NUMBER'])
    self.vphone.save()

    self.id = cid

    self.num = args['NUMBER']
    self.backend = 'VirtualPhone'


def __delete__(self):
    self.vphone.
