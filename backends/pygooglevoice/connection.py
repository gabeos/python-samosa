from backends.pygooglevoice.util import gv_convos_to_messages
from core import MessageSet
from settings import GV_USER, GV_PASSWORD
from googlevoice import Voice

class Connection():
    """Manages connection with Google Voice"""
    
    def get_messages(self):
        return gv_convos_to_messages(self.voice)
    
    def __init__(self):
        self.voice = Voice()
        self.voice.login(email=GV_USER,passwd=GV_PASSWORD)
        
    def __delete__(self):
        self.voice.logout()
