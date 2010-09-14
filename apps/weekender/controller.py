from apps.weekender.models import *
from util.models import Log
import apps.weekender.responses
import re

#define the app's behavior in the form of test / response pairs


#first define tests as functions that are given a Message object
#and perform arbitary evaluations, returning True or False
#(returning None is also evaluated as False)

def unread(message):
    return not Log.objects(m_id=message.id) and message.from_num != message.connection.num

def join(message):
    return "#join#" in message.text.lower() and unread(message)

def is_subscribed(message):
    return bool(Phone.objects(number=message.from_num,subscribed=True))

def subscribe(message):
    return join(message) and not is_subscribed(message)

def already_subscribed(message):
    return join(message) and is_subscribed(message)

def unsubscribe(message):
    return "#unsubscribe#" in message.text.lower() and (unread(message) and is_subscribed(message))

def announce(message):
    return bool(re.search(r'#announce[ _\-#]?this#',message.text.lower())) and unread(message)    

#Here associate tests with responses
reactions = (
                (subscribe, apps.weekender.responses.subscribe),
                (already_subscribed, apps.weekender.responses.already_subscribed),
                (unsubscribe, apps.weekender.responses.unsubscribe),
                (announce, apps.weekender.responses.announce),
            )
