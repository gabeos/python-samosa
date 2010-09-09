from core.message import Message
from util.models import Log

import mongoengine as ME
ME.connect("joke")

def tell_joke(message):
    from simplejson import load
    jokes = load(open("apps/joke/jokes.json"))
    from random import choice
    joke = choice(jokes)
    print "Sending a joke to %s" % message.from_num
    reply = Message(id="%s_joke" % message.id,to_num = message.from_num, from_num = message.to_num, text = joke)

    Log(message).save()
    Log(reply).save()

    message.connection.send(reply)

    
