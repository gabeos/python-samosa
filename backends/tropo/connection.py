from backends.tropo.util import TropoHelper
from core.message_set import MessageSet
from core.connection import Connection as SuperConn

class Connection(SuperConn):
    """holds messages from Tropo to be consumed by get_messages.
       sends messages out through Tropo."""

    def get_messages(self):
        """Retrieves messages from the tropo helper"""
        mmm = self.tropo_helper.get_new_messages()
        if len(mmm) > 0:
            print "I got %s"%[m.from_num+":"+m.text for m in mmm]
        return mmm

    def send(self,msg):
        """Sends a text message through tropo."""
        return self.tropo_helper.send_message(msg)

        
    def __init__(self,cid,**args):
        """Connection to Tropo.
        kwargs:
            TOKEN  = outgoing tropo authentication token"""
    
        self.id = cid
        self.token = args['TOKEN']
        self.backend = 'tropo'
        
        if 'NUMBER' in args.keys():
            self.num = args['NUMBER']
        else:
            self.num = "hrothgar@tropo.im"
        
        self.tropo_helper = TropoHelper(self)
        self.tropo_helper.start()


