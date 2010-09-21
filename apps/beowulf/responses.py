from core.message import Message
from util.wakeupcall import call_all
from util.models import Log
import os.path
import re
import mongoengine as ME

ME.connect("beowulf")

TEXT_FILE ="apps/beowulf/beowulf.txt"
WAV_BASE ="apps/beowulf/beowav"
NO_MATCH_WAV_FILE="apps/beowulf/sounds/myst.wav"
KEYWORD = "beo "



def match_line(message):
    request = message.text.lower()[len(KEYWORD):].strip().splitlines()[0]
    matches = [(i+1,line) for (i,line) in enumerate(open(TEXT_FILE))
                                                if request in line.lower()]
                                                
                                                
    match_wav_file = NO_MATCH_WAV_FILE
    if matches:
        matched_line = "line %d: %s" % matches[0]
        for name in os.listdir(WAV_BASE):
            bounds = re.findall("\d+", name)
            if(len(bounds) == 2 and int(bounds[0]) <= matches[0][0] and int(bounds[1]) >= matches[0][0]):
                match_wav_file = os.path.join(WAV_BASE, name)
    else:
        matched_line = "no match!"
    
    print "Sending line from Beowulf to %s: %s" % (message.from_num, matched_line)
    
    
    call_all_thread([message.from_num], [match_wav_file])
    # Place the call,  wait for call to end.
    #what happens if we try to start before we're finished with another call?
    
    reply = Message(id="beowulf",to_num = message.from_num, from_num = message.to_num, text = matched_line)
    reply.connection = message.connection
    reply.send()
    #TODO: a generalized way to alter messages so we can mark it read
    #--though apparently GV eventually marks something as read if it has been replied to
    #so this tends to send twice only?
    
    Log(message).save();
    Log(reply).save();

