from apps.group_demo.responses import KEYWORD, group_call
from util.models import Log
import mongoengine as ME
from datetime import datetime

#define the app's behavior in the form of test / response pairs


#first define tests as functions that are given a Message object
#and perform arbitary evaluations, returning True or False
#(returning None is also evaluated as False)

start = datetime.now().replace(second=0)

def is_new(message):
    ME.connect("group_demo")
    return not message.is_read and not Log.objects.filter(m_id=message.id) and message.datetime > start

def is_group_call_request(message):
    if (message.text.lower().startswith(KEYWORD) and is_new(message)):
        return True

#Here associate tests with responses
reactions = (
                (is_group_call_request, group_call),
            )
