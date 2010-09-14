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

    text = re.sub(r'#announce[ _\-#]?this#',message.from_num[2:]+"WKND:",message.text.lower(), re.I)
    for phone in phones:
        announce = Message(to_num = phone.number, from_num = message.to_num, text = text)
        Log(announce).save()
        message.connection.send(announce)

    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "Your announcement has been sent.")

    Log(reply).save()
    Log(message).save()
    message.connection.send(reply)


def register_expert(message):
    
    print "Registering %s as expert" % message.from_num

    p = Phone.objects.get_or_create(number=message.from_num)
    p.expert=True
    p.save()

    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "The number %s has been registered as an expert for the Weekender. To unsubscribe at any time text #UNREGISTER EXPERT# to %s." % (message.from_num,message.to_num))

    reply2 = Message(to_num = message.from_num, from_num = message.to_num, text = "Instructions: As an expert you will be sent questions from various Weekenders in the format 'qstn#..# QUESTION'. If you have an answer, reply to %s in the following format: #ANSWER# <last 4 digits of number in qstn> <answer>" % message.to_num)

    Log(message).save()
    Log(reply).save()
    
    message.connection.send(reply)
    message.connection.send(reply2)


def already_expert(message):
    
    print "%s tried to register as an expert twice" % message.from_num

    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "The number, %s, has already been registered as an expert for the Weekender. If you want to *un*subscribe, text #UNREGISTER EXPERT# to %s." % (message.from_num, message.to_num))

    Log(message).save()
    Log(reply).save()

    message.connection.send(reply)


def unregister_expert(message):

    print "Unregistering %s as expert" % message.from_num

    p = Phone.objects.get_or_create(number=message.from_num)
    p.expert = False
    p.save()

    reply = Message(to_num=message.from_num, from_num=message.to_num, text="The number %s has been unregistered as an expert. To re-register, text #REGISTER EXPERT# to %s." % (message.from_num, message.to_num))

    Log(message).save()
    Log(reply).save()
    message.connection.send(reply)


def ask_question(message):

    print "%s is asking the question: \"%s\"" % (message.from_num, message.text[6:])

    sender = Phone.objects(subscribed=True,number=message.from_num)
    if not sender:
        subscribe(message) #this creates duplicate log entries

    qstn_text = re.sub(r'#ask#', "qstn" + message.from_num, message.text, re.I)

    Log(message).save()

    push_to_experts(qstn_text, (message.from_num,))

    reply = Message(from_num=message.to_num, to_num=message.from_num, text="Your question has been distributed. Hopefully one of the local experts will get back to you soon!")

    Log(reply).save()

def answer_question(message):
    
    answer_match = re.search(r'#answer#\s*(\d{4,})\s*(.*)', message.text)
    number_code = answer_match.group(1)
    answer_text = answer_match.group(2)

    print "%s in answering the question asked by %s" % (message.from_num, number_code)

    asker = Phone.objects(subscribed=True, number__endswith=number_code)
    if not asker:
        #send incorrect code msg
        incorrect_code_message = Message(from_num=message.to_num, to_num=message.from_num, text="I'm sorry, no subscriber could be found with phone number ending in %s. Please check your digits and try again with format #ANSWER# <NUMBER> <ANSWER TEXT>" % number_code)
        Log(incorrect_code_message).save()
        message.connection.send(incorrect_code_message)
    
    elif asker.count() > 1:
        #send more than one matched number code
        multiple_matches_message = Message(from_num=message.to_num, to_num=message.from_num, text="I'm sorry, but there were more than one subscribers with phone # ending in the digits %s. Please re-send the message with more digits from the original question. Thanks!" % number_code)
        Log(multiple_matches_message).save()
        message.connection.send(multiple_matches_message)

    else:
        answer_message = Message(from_num=message.to_num, to_num=asker.number, text = "ANSWER: " + answer_text)
        Log(answer_message).save()
        message.connection.send(answer_message)
        push_to_experts("ANSWER:" + answer_text, (message.from_num,))

def push_to_experts(text, exceptions=None):
    """Sends message containing 'text' to all experts except those listed in exceptions"""
    
    experts = Phone.objects(expert=True,number__nin=exceptions)
    for expert in experts:
        qstn_message = Message(to_num=expert.number, from_num=message.to_num, text = qstn_text)

        Log(qstn_message).save()
        message.connection.send(qstn_message)

        
