from core.message import Message

def tell_joke(message):
    from simplejson import load
    jokes = load(open("apps/joke/jokes.json"))
    from random import choice
    joke = choice(jokes)
    print "Sending a joke to %s" % message.from_num
    m = Message(id="joke",to_num = message.from_num, from_num = message.to_num, text = joke)
    m.connection = message.connection
    m.send()
    #TODO: a generalized way to alter messages so we can mark it read
    #--though apparently GV eventually marks something as read if it has been replied to
    #so this tends to send twice only?
