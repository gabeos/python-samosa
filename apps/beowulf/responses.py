from core.message import Message


BEOWULF_FILE ="apps/beowulf/beowulf.txt"
KEYWORD = "beo "

def match_line(message):
    request = message.text.lower()[len(KEYWORD):].strip().splitlines()[0]
    print "request: "+request
    matched_line = "no match!"
    for line in open(BEOWULF_FILE):
        if (request in line.lower()):
            matched_line = line
            break
    
    #matched_line = call(['grep', message, '/Users/dadamson/lab/python-samosa/apps/beowulf/beowulf.txt'])
    
    print "Sending a line from Beowulf to %s" % message.from_num
    print matched_line
    
    m = Message(id="beowulf",to_num = message.from_num, from_num = message.to_num, text = matched_line)
    m.connection = message.connection
    m.send()
    #TODO: a generalized way to alter messages so we can mark it read
    #--though apparently GV eventually marks something as read if it has been replied to
    #so this tends to send twice only?
