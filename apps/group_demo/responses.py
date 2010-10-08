from util.wakeupcall import call_all, call_all_thread
from util.models import Log
import mongoengine as ME
import re


MYSTERIOUS_WAV_FILE="apps/beowulf/sounds/myst.wav"
WAIT_FILE = "apps/group_demo/sounds/wait.wav"
KEYWORD = "group call "

#todo: remake in the image of weekender, plus groups

def skypeify(phone):
    if re.match("^\d{10}$", phone):
        phone = "+1"+phone
    return phone
    #this will leave non-numbers like echo123 in place for testing

def group_call(message):
    targets = map(skypeify, message.text.lower()[len(KEYWORD):].splitlines()[0].strip().split())
        
    if message.from_num not in targets:
        targets.append(message.from_num)
    
    print "Sending a mysterious message to %s" % targets
    
    ME.connect("group_demo")
    Log(message).save();
    
    #third parameter is optional, and will be played if the first target picks up before the rest
    call_all_thread(targets, [MYSTERIOUS_WAV_FILE], WAIT_FILE)
    
    print "done calling call-all!" 

