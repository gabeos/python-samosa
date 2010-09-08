from core.message import Message
from apps.weekender.models import *
from util.models import Log

def subscribe(message):
    print "Subscribing %s" % message.from_num

    try:
        p = Phone.objects.get(number=message.from_num)
    except DoesNotExist:
        p = Phone(number=message.from_num)
    p.subscribed = True
    p.save()

    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "The number %s has been subscribed to the Weekender announcement list. To unsubscribe at any time text #UNSUBSCRIBE# to %s." % (message.from_num,message.to_num))
    reply.connection = message.connection
    reply.send()
