from core.message import Message
from core.message_set import MessageSet
from apps.weekender.models import *
from util.models import Log
import re

def subscribe(message):
    print "Subscribing %s" % message.from_num

    p = Phone.objects.get_or_create(number=message.from_num)
    p.subscribed = True
    p.save()

    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "The number %s has been subscribed to the Weekender announcement list. To unsubscribe at any time text #UNSUBSCRIBE# to %s." % (message.from_num,message.to_num))

    Log(message).save()
    Log(reply).save()
    message.connection.send(reply)

def already_subscribed(message):
    print "%s tried to subscribe twice." % message.from_num

    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "The number %s is already subscribed to the Weekender announcement list. Wanna *un*subscribe? Just text #UNSUBSCRIBE# to %s." % (message.from_num,message.to_num))

    Log(message).save()
    Log(reply).save()
    message.connection.send(reply)

def unsubscribe(message):
    print "Unsubscribing %s" % message.from_num

    p = Phone.objects.get(number=message.from_num)
    p.subscribed = False
    p.save()

    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "The number %s has been unsubscribed to the Weekender announcement list. To re-subscribe just text #JOIN# to %s." % (message.from_num,message.to_num))

    Log(message).save()
    Log(reply).save()
    message.connection.send(reply)

def announce(message):
    print "%s sending announcement \"%s\"" % (message.from_num, message.text[15:])

    sender = Phone.objects(subscribed=True,number=message.from_num)
    if not sender:
        subscribe(message) #this creates duplicate log entries

    phones = Phone.objects(subscribed=True,number__ne=message.from_num)

    text = re.sub(r'#announce[ _\-#]?this#',message.from_num[2:]+"WKND:",message.text.lower())
    for phone in phones:
        announce = Message(to_num = phone.number, from_num = message.to_num, text = text)
        Log(announce).save()
        message.connection.send(announce)

    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "Your announcement has been sent.")

    Log(reply).save()
    Log(message).save()
    message.connection.send(reply)

