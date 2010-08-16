from settings import APPS
from time import sleep
from threading import Thread, Event
from random import randint

REQUIRED_MSG_ATTRS = (
                'from_num',
                'to_num',
                'text',
                 )
    
OPTIONAL_MSG_ATTRS = (
                'id',
                'labels',
                'datetime',
                'is_read',
                'backend',
                 )

class Message(object):
    """Message objects. Should hold common attributes available
    from different backends."""
    
    def __init__(self,**kwargs):
        
        for attr in REQUIRED_MSG_ATTRS:
            if not kwargs.has_key(attr):
                raise Exception('%s is a required attribute of Message object' % attr)
            setattr(self,attr,kwargs[attr])
            del kwargs[attr]
            
        for attr,val in kwargs.iteritems():
            if attr not in OPTIONAL_MSG_ATTRS:
                raise Exception('%s is an unknown attribute of Message object' % attr)
            setattr(self,attr,kwargs[attr])
            
    def __repr__(self):
        return "<Message from %s to %s>" % (self.from_num, self.to_num)
            
                
class MessageSet(list):
    """extend basic list to provide query methods over a list of messages"""
    
    def filter(self,**kwargs):
        """Returns only Messages matching specified attributes
        as new MessageSet instance.
            MessageSet.filter(attr1=val1,attr2=val2)
        is functionally equivalent to
            MessageSet.filter(attr1=val1).filter(attr2=val2)

        Message.labels is treated specially:
            MessageSet.filter(labels=['starred'])
        returns messages if ('starred' in Message.labels)

        For union over labels use:
            MessageSet.filter(labels=['starred','spam'])
        For intersection use:
            MessageSet.filter(labels=['starred']).filter(['spam'])"""
            
        
        tempMS = MessageSet(self)
        #handle labels attribute with union instead of equivalence
        if kwargs.has_key('labels'):
            if isinstance(kwargs['labels'],str):
                 kwargs['labels'] = [kwargs['labels']]
            tempMS = [m for m in tempMS if set(m.labels).union(kwargs['labels'])]
            del kwargs['labels']
        for attr,val in kwargs.iteritems():
            if attr not in REQUIRED_MSG_ATTRS + OPTIONAL_MSG_ATTRS:
                raise Exception('%s is an unknown attribute of Message object' % attr)
            tempMS = [m for m in tempMS if m.__getattribute__(attr) == val]
            
        return tempMS

    #should possibly define this by using XOR with MS.filter for guaranteed consistency?
    def exclude(self,**kwargs):
        """Returns only Messages NOT matching specified attributes
        as new MessageSet instance.
            MessageSet.exclude(attr1=val1,attr2=val2)
        is functionally equivalent to
            MessageSet.exclude(attr1=val1).exclude(attr2=val2)

        Message.labels is treated specially:
            MessageSet.exclude(labels=['starred'])
        returns messages if ('starred' not in Message.labels)

        For union over labels use:
            MessageSet.exclude(labels=['starred','spam'])
        For intersection use:
            MessageSet.exclude(labels=['starred']).exclude(['spam'])"""

        if kwargs.has_key('labels'):
            if isinstance(kwargs['labels'],str):
                 kwargs['labels'] = [kwargs['labels']]
            tempMS = [m for m in tempMS if not set(m.labels).union(kwargs['labels'])]
            del kwargs['labels']
        tempMS = MessageSet(self)
        for attr,val in kwargs.iteritems():
            if attr not in REQUIRED_MSG_ATTRS + OPTIONAL_MSG_ATTRS:
                raise Exception('%s is an unknown attribute of Message object' % attr)
            tempMS = [m for m in tempMS if m.__getattribute__(attr) != val]
            
        return tempMS
       
    def get(self,**kwargs):
        """Shortcut method for MessageSet.filter(**kwargs)[0]"""
        
        res = self.filter(kwargs)
        if len(res) != 1:
            raise Exception('More than one message matched using criteria: %s' % kwargs)
        return res[0]
        
    def unread(self):
        """Shortcut for MessageSet.filter(is_unread=True)."""
        return self.filter(is_unread=True)
        
    def __repr__(self):
        if len(self) < 10:
            return str(self)
        else:
            return "[%s...]" % ', '.join([str(m) for m in self[:6]])

class Connection(object):
    """Superclass for each backend's Connection object."""
    
    def __init__(self):
        pass

    def __repr__(self):
        return "<%s Connection for %s at %s>" % (self.backend, self.id, self.num)
        
    def len():
        return None
        
        
class ConnectionSet(list):
    """Holds multiple connections in one contatiner and
    provides bulk access to common methods of its elements."""

    def get_messages(self):
        return MessageSet(m for conn in self for m in conn.get_messages())
        

class Checker(Thread):
    """Checks messages and passes results to associated apps."""

    def __init__(self,c_set,interval):
        Thread.__init__(self)
        self.event = Event()
        self.connection_set = c_set
        self.interval = interval
        self.done = False

    def check(self):
        print "Checking %s" % self.connection_set
        msgs = self.connection_set.get_messages()
        print msgs

    def run(self):
        while not self.done:
            self.check()
            #if interval is a tuple, take that as a range from which
            #to pick a random wait time
            if isinstance(self.interval,tuple):
                self.event.wait(randint(self.interval[0],self.interval[0]))
            else:
                self.event.wait(interval)

    def stop(self):
        self.done = True
