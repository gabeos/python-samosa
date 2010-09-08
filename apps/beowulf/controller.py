import apps.beowulf.responses 
from datetime import datetime, date, time

#define the app's behavior in the form of test / response pairs


#first define tests as functions that are given a Message object
#and perform arbitary evaluations, returning True or False
#(returning None is also evaluated as False)

last_time = datetime.now().replace(second=0, microsecond=0) #the last timestamp we read - only precise to the minute
consumed_ids = [] #messages consumed in the current minute

def is_new(message):
    if message.datetime > apps.beowulf.controller.last_time:
        #print "new: %s at %s" % (message.id, message.datetime)
        return True;
    elif message.datetime < apps.beowulf.controller.last_time:
        return False;
    else:
        #if message.id not in apps.beowulf.controller.consumed_ids: 
            #print "new this minute: %s at %s" % (message.id, message.datetime)
            #print apps.beowulf.controller.consumed_ids
        return message.id not in apps.beowulf.controller.consumed_ids

def remember(message):
    if(message.datetime > apps.beowulf.controller.last_time):
        apps.beowulf.controller.consumed_ids = []
        
    apps.beowulf.controller.consumed_ids.append(message.id)    
    apps.beowulf.controller.last_time = message.datetime

def is_match_request(message):
    if (message.text.lower().startswith(apps.beowulf.responses.KEYWORD) and is_new(message)):
        remember(message)
        return True
        
    else:
        return False


#Here associate tests with responses
reactions = (
                (is_match_request, apps.beowulf.responses.match_line),
            )
