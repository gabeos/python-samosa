import apps.joke.responses
from util.models import Log

#define the app's behavior in the form of test / response pairs


#first define tests as functions that are given a Message object
#and perform arbitary evaluations, returning True or False
#(returning None is also evaluated as False)

def is_joke(message):
    if "#joke" in message.text.lower() and not Log.objects.filter(m_id=message.id):
        return True


#Here associate tests with responses
reactions = (
                (is_joke, apps.joke.responses.tell_joke),
            )
