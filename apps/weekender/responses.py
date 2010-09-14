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

    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "The number %s has been subscribed to the Weekender announcement list. To unsubscribe at any time text 'surfer leave' to %s." % (message.from_num,message.to_num))

    Log(message).save()
    Log(reply).save()
    message.connection.send(reply)

def already_subscribed(message):
    print "%s tried to subscribe twice." % message.from_num

    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "The number %s is already subscribed to the Weekender announcement list. Wanna *un*subscribe? Just text 'surfer leave' to %s." % (message.from_num,message.to_num))

    Log(message).save()
    Log(reply).save()
    message.connection.send(reply)

def unsubscribe(message):
    print "Unsubscribing %s" % message.from_num

    p = Phone.objects.get(number=message.from_num)
    p.subscribed = False
    p.save()

    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "The number %s has been unsubscribed to the Weekender announcement list. To re-subscribe just text 'surfer join' to %s." % (message.from_num,message.to_num))

    Log(message).save()
    Log(reply).save()
    message.connection.send(reply)

def announce(message):
    print "%s sending announcement \"%s\"" % (message.from_num, message.text[15:])

    sender = Phone.objects(subscribed=True,number=message.from_num)
    if not sender:
        subscribe(message) #this creates duplicate log entries

    phones = Phone.objects(subscribed=True,number__ne=message.from_num)

    text = re.sub(r'surfer announce',message.from_num[2:]+"WKND:",message.text.lower(), re.I)
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

    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "The number %s has been registered as an expert for the Weekender. To unsubscribe at any time text 'surfer expert leave' to %s." % (message.from_num,message.to_num))

    reply2 = Message(to_num = message.from_num, from_num = message.to_num, text = "Instructions: As an expert you will be sent questions from various Weekenders in the format 'WKND_QSTN <shortcode>: QUESTION'. If you have an answer, reply to %s in the format: 'surfer answer <shortcode> <answer>'" % message.to_num)

    Log(message).save()
    Log(reply).save()
    
    message.connection.send(reply)
    message.connection.send(reply2)


def already_expert(message):
    
    print "%s tried to register as an expert twice" % message.from_num

    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "The number, %s, has already been registered as an expert for the Weekender. If you want to *un*subscribe, text 'surfer expert leave' to %s." % (message.from_num, message.to_num))

    Log(message).save()
    Log(reply).save()

    message.connection.send(reply)


def unregister_expert(message):

    print "Unregistering %s as expert" % message.from_num

    p = Phone.objects.get_or_create(number=message.from_num)
    p.expert = False
    p.save()

    reply = Message(to_num=message.from_num, from_num=message.to_num, text="The number %s has been unregistered as an expert. To re-register, text 'surfer expert join' to %s." % (message.from_num, message.to_num))

    Log(message).save()
    Log(reply).save()
    message.connection.send(reply)


def ask_question(message):

    print "%s is asking the question: \"%s\"" % (message.from_num, message.text[15:])

    sender = Phone.objects(subscribed=True,number=message.from_num)
    if not sender:
        subscribe(message) #this creates duplicate log entries

    qstn_text = re.sub(r'surfer question', "WKND_QSTN " + get_short_code(message.from_num) + ":", message.text, re.I)

    Log(message).save()

    push_to_experts(qstn_text, (message.from_num,))

    reply = Message(from_num=message.to_num, to_num=message.from_num, text="Your question has been distributed. Hopefully one of the local experts will get back to you soon!")

    Log(reply).save()

def answer_question(message):
    
    answer_match = re.search(r'surfer\s*answer\s*(\d+)\s*(.*)', message.text)
    if answer_match:
        number_code = answer_match.group(1)
        answer_text = answer_match.group(2)
    
    else:
        incorrect_format_message = Message(from_num=message.to_num, to_num=message.from_num, text="I'm sorry, I could not understand your text. Remember to use the format 'surfer answer <shortcode> <answer>'")
        Log(incorrect_format_message).save()
        message.connection.send(incorrect_format_message)

    print "%s in answering the question asked by %s" % (message.from_num, number_code)

    asker = Phone.objects(subscribed=True, number__endswith=number_code)
    if not asker:
        #send incorrect code msg
        incorrect_code_message = Message(from_num=message.to_num, to_num=message.from_num, text="I'm sorry, no subscriber could be found with phone number ending in %s. Please check your digits and try again with format 'surfer answer <shortcode> <answer>'" % number_code
        Log(incorrect_code_message).save()
        message.connection.send(incorrect_code_message)
    
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

        

def get_short_code(number):
    """gets shortest code that uniquely specifies number in db starting from rightmost digits"""

    for rev_index in range(-1,-len(number),-1):
        shortcode = number[rev_index:]

        if not Phone.objects(number__ne=number, number__endswith=shortcode):
            return shortcode

    return number
