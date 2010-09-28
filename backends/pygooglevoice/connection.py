from backends.pygooglevoice.util import gv_convos_to_messages
from core.message_set import MessageSet
from core.connection import Connection as SuperConn
from googlevoice import Voice

class Connection(SuperConn):
    """Manages connection with Google Voice"""
    
    def get_messages(self):
        """Retrieve messages from GV connection and return MessageSet instance"""
        return gv_convos_to_messages(self)
        
    def send(self,msg):
        """Send a message using this GV connection."""
        #Should we check if it's sending a message to itself?
        
        self.check_num_format(msg.to_num) #raises exception if not right format
        
        self.voice.send_sms(msg.to_num,msg.text)
        
    def __init__(self,cid,**creds):
        """Connection to Google Voice.
        optional keyword args:
            GV_USER=<str>, GV_PASSWORD=<str>
        (if none provided will prompt)"""
        
        self.voice = Voice()
        print "logging in to GV account %s" % creds['GV_USER']
        self.voice.login(email=creds['GV_USER'],passwd=creds['GV_PASSWORD'])
        self.id = cid
        self.num = self.voice.settings['primaryDid']
        self.backend = 'pygooglevoice'
        
    def __delete__(self):
        self.voice.logout()
