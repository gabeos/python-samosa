import collections
from core import *

class OrderedMessageSet(collections.MutableSet):
    """Set of Messages that preserves order
    
        Implemented with list to preserve order 
        and dict to preserve uniqueness of elements
    """
     
    def __init__(self, init_list=[]):
        self._map = {}
        self.messages = []
        if init_list:
            self.add_list(init_list)
        
    def __iter__(self):
        return iter(self.messages)
    
    def __contains__(self, message):
        return message in self.elements
    
    def __len__(self):
        return len(elements)
    
    def add(self, message):
        if not isinstance(message, Message):
            raise TypeError("Item not of type Message")
        if self._map[message.id]:
            raise KeyError("Message already in set")
        
        for i in range(len(self.messages)):             
            if cmp(self.messages[i], message) > 0:
                self.messages.insert(i, message)
                break
        else:
            self.messages.append(message)

        self._map[message.id] = 1;
    
    def add_list(self, message_list):
        for message in message_list:
            try:
                self.add(message)
            except (TypeError, KeyError):
                pass
                
    
    def discard(self, message):
        self._map.pop(message.id)
        self.messages.remove(message)
    
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

        tempMS = OrderedMessageSet(init_list=self.messages)
        
        if kwargs.has_key('labels'):
            if isinstance(kwargs['labels'],str):
                 kwargs['labels'] = [kwargs['labels']]
            tempMS = OrderedMessageSet(init_list=[m for m in tempMS if not set(m.labels).union(kwargs['labels'])])
            del kwargs['labels']
        for attr,val in kwargs.iteritems():
            if attr not in REQUIRED_MSG_ATTRS + OPTIONAL_MSG_ATTRS:
                raise Exception('%s is an unknown attribute of Message object' % attr)
            tempMS = OrderedMessageSet(init_list=[m for m in tempMS if m.__getattribute__(attr) != val])
            
        return tempMS
    
    def filter(self, **kwargs):
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
            
        tempMS = OrderedMessageSet(init_list=self.messages)
        #handle labels attribute with union instead of equivalence
        if kwargs.has_key('labels'):
            if isinstance(kwargs['labels'],str):
                 kwargs['labels'] = [kwargs['labels']]
            tempMS = OrderedMessageSet(init_list=[m for m in tempMS if set(m.labels).union(kwargs['labels'])])
            del kwargs['labels']
        for attr,val in kwargs.iteritems():
            if attr not in REQUIRED_MSG_ATTRS + OPTIONAL_MSG_ATTRS:
                raise Exception('%s is an unknown attribute of Message object' % attr)
            tempMS = OrderedMessageSet(init_list=[m for m in tempMS if m.__getattribute__(attr) == val])
            
        return tempMS
    
    def get(self, message_id):
        for e in self.messages:
            if message_id == e.id:
                return e
            
    def pop(self, index=0):
        """If no index is specified, returns the most recent message"""
        
        self._map.pop(self.messages[index])
        return self.messages.pop(index)
    

    @classmethod
    def union(cls, SetA, SetB):
        SetC = OrderedMessageSet(SetA.messages)
        SetC.add_list(SetB.messages)
        return SetC
    
    @classmethod
    def intersection(cls, SetA, SetB):
        SetC = OrderedMessageSet()
        for ma in SetA._map.keys():
            if SetB._map.has_key(ma):
                SetC.add(SetA.get(ma))
        return SetC
    
    @classmethod
    def isdisjoint(cls, SetA, SetB):
        for ma in SetA._map.keys():
            if SetB._map.has_key(ma):
                return False;