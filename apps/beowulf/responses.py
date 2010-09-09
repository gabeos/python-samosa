from core.message import Message


BEOWULF_FILE ="apps/beowulf/beowulf.txt"
KEYWORD = "beo "

def match_line(message):
    request = message.text.lower()[len(KEYWORD):].strip().splitlines()[0]
    matches = [(i+1,line) for (i,line) in enumerate(open(BEOWULF_FILE))
                                                if request in line.lower()]
    if matches:
        matched_line = "line %d: %s" % matches[0]
    else:
        matched_line = "no match!"
    
    print "Sending line %d from Beowulf to %s" % (line_number, message.from_num)
    
    m = Message(id="beowulf",to_num = message.from_num, from_num = message.to_num, text = matched_line)
    m.connection = message.connection
    m.send()
    #TODO: a generalized way to alter messages so we can mark it read
    #--though apparently GV eventually marks something as read if it has been replied to
    #so this tends to send twice only?
