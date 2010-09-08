import apps.weekender.responses

#define the app's behavior in the form of test / response pairs


#first define tests as functions that are given a Message object
#and perform arbitary evaluations, returning True or False
#(returning None is also evaluated as False)

def subscribe(message):
    if "#join#" in message.text.lower() and not message.is_read:
        return True


#Here associate tests with responses
reactions = (
                (subscribe, apps.weekender.responses.subscribe),
            )
