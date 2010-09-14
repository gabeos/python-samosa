from apps.beowulf.responses import KEYWORD, match_line
from util.models import Log
from datetime import datetime

#define the app's behavior in the form of test / response pairs


#first define tests as functions that are given a Message object
#and perform arbitary evaluations, returning True or False
#(returning None is also evaluated as False)

def is_new(message):
    return not message.is_read and not Log.objects.filter(m_id=message.id)

def is_match_request(message):
    if (message.text.lower().startswith(KEYWORD) and is_new(message)):
        return True
    else: return False


#Here associate tests with responses
reactions = (
                (is_match_request, match_line),
            )
