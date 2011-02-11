#!/usr/bin/env python

# Sample application using the itty-bitty python web framework from:
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

    def __init__(self, connection):
        self.msgs = MessageSet()
        self.cxn = connection
        threading.Thread.__init__(self)

    #set up
    def run(self):       

        @post('/index.json')
        def send(request):
            s = Session(request.body)
            t = Tropo()
            
            print s.initialText
            
            #outgoing messages go to tropo and straight back to us so we can handle them?
            if  hasattr(s, 'parameters') and 'outgoing' in s.parameters.keys(): 
                t.call(s.parameters['to_num'], channel="TEXT")
                t.say(s.parameters['message'])
    
            else: #build a new message representation
                m = Message(from_num=s.fromaddress['id'],
                          to_num=s.to['id'],
                          text=s.initialText,
                          id=s.id,
                          labels=None,
                          datetime=datetime.now(), #should convert s.timestamp
                          is_read = True,
                          connection = self.cxn)
                self.msgs.append(m)
                
            
            return t.RenderJson()
            
        run_itty(server='wsgiref', host='0.0.0.0', port=8888)        
        
    def get_new_messages(self):
        new_messages = self.msgs
        if len(new_messages) > 0:
            self.msgs = MessageSet()
        return new_messages
        
    #outgoing messages go to tropo and straight back to us so we can handle them? Is there a better way?
    def send_message(self, msg):
        base_url = 'http://api.tropo.com/1.0/sessions'
        token = '14b1c3f6aaf27b46aa008acb4e7c779bf2b986b194f2e1a1ffb160770c34a3af4dff141f42caec47489ff030'	
        action = 'create'
        number  = msg.to_num
        message = msg.text
        
        params = urlencode([('action', action), ('token', token), ('to_num', number), ('message', message), ('outgoing', True)])
        urlopen('%s?%s' % (base_url, params))
        print "message sent!"
        
    