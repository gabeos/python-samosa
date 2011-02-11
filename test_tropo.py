from backends.tropo.util import TropoHelper
from core.message import Message
import time
import sys

monkey = TropoHelper(None)
monkey.start()

print "starting listener loop"

#monkey.send_message(Message(from_num="14107010048",to_num="14107010048", text="booyah!"))

try:
    while(True):
        mmm = monkey.get_new_messages()
        if len(mmm) > 0:
            print "messages: %s\n"%([m.from_num+": "+m.text for m in mmm])
            for m in mmm:
                monkey.send_message(Message(from_num=m.to_num, to_num=m.from_num, text="!!"+m.text))
        time.sleep(3)
        
except (KeyboardInterrupt, SystemExit):
    pass
    
sys.exit(0) #the itty-thread doesn't want to die...