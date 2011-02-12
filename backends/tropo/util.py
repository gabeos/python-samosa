#!/usr/bin/env python

# using the itty-bitty python web framework from:
#  http://github.com/toastdriven/itty

import threading
from itty import *
from datetime import *
from tropo import Tropo, Session, Say
from core.message_set import MessageSet
from core.message import Message
from urllib import urlencode
from urllib2 import urlopen


                
class TropoHelper(threading.Thread):
    """starts up an http server to handle messages to and from Tropo"""

    def __init__(self, connection):
        self.msgs = MessageSet()
        self.cxn = connection
        threading.Thread.__init__(self)

    #set up handler for posts from Tropo
    def run(self):       

        @post('/index.json')
        def send(request):
            s = Session(request.body)
            t = Tropo()
            
            print s.dict
            
            #outgoing messages from the Session API.
            if  hasattr(s, 'parameters') and  s.parameters.has_key('outgoing'): 
                 
                t.call(to=s.parameters['to_num'], channel='TEXT', network=s.parameters['network'])
                t.say(s.parameters['message'])
                print "message sent!"
    
            elif s.fromaddress['channel'] == 'TEXT': #receive a message, build a new Message, and add it to the MessageSet.
                m = Message(from_num=s.fromaddress['id'],
                          to_num=s.to['id'],
                          text=s.initialText,
                          id=s.id,
                          datetime=datetime.now(), #should convert s.timestamp to datetime
                          is_read = False, #True? what is the state of a freshly-arrived message?,
                          connection = self.cxn)
                          
                self.msgs.append(m)
                
            #tell tropo to do our dirtywork - for receiving messages, this does nothing.
            return t.RenderJson()
        
        #run an itty bitty webserver. 
        run_itty(server='wsgiref', host='0.0.0.0', port=8888)        
        
    #return new messages since the last call, and chuck the rest.
    def get_new_messages(self):
        new_messages = self.msgs
        if len(new_messages) > 0:
            self.msgs = MessageSet()
        return new_messages
        
    #outgoing messages are sent to tropo and straight back to us so we can handle them? Is there a better way?
    def send_message(self, msg):
        base_url = 'http://api.tropo.com/1.0/sessions'
        token = '14b1c3f6aaf27b46aa008acb4e7c779bf2b986b194f2e1a1ffb160770c34a3af4dff141f42caec47489ff030' # self.cxn.token #
        action = 'create'
        number  = msg.to_num
        message = msg.text
        
        #maybe replace this with a mapping from the network given to incoming numbers
        
        if number[1:].isdigit():
            network = 'SMS'
        else:
            network = 'JABBER'
        
        params = urlencode([('action', action), 
                            ('token', token), 
                            ('to_num', number), 
                            ('message', message), 
                            ('network', network), 
                            ('outgoing', True),])
        urlopen('%s?%s' % (base_url, params))
        
    