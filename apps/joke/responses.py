def tell_joke(message):
    from simplejson import load
    jokes = load(open('/home/askory/Scripts/samosa/apps/joke/jokes.json'))
    from random import choice
    joke = choice(jokes)
    print "\n\nI WOULD be telling: \"%s\" to %s IF sending was implemented...\n" % (joke, message.from_num)
    #TODO: a generalized way to alter messages so we can mark it read 
