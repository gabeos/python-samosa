REQUIRED_ATTRS = (
                'from_num',
                'to_num',
                'text',
                 )
    
OPTIONAL_ATTRS = (
                'id',
                'labels',
                'datetime',
                'is_read',
                'backend',
                 )

class Message(object):
    """Message objects."""
    
    def __init__(self,**kwargs):
        
        for attr in REQUIRED_ATTRS:
            if not kwargs.has_key(attr):
                raise Exception('%s is a required attribute of Message object' % attr)
            setattr(self,attr,kwargs[attr])
            del kwargs[attr]
            
        for attr,val in kwargs.iteritems():
            if attr not in OPTIONAL_ATTRS:
                raise Exception('%s is an unknown attribute of Message object' % attr)
            setattr(self,attr,kwargs[attr])
            
                
class MessageSet(list):
    """extend basic list to provide query methods over a list of messages"""
    
    def filter(self,**kwargs):
        tempMS = MessageSet(self)
        #handle labels attribute with union instead of equivalence
        if kwargs.has_key('labels'):
            if isinstance(kwargs['labels'],str):
                 kwargs['labels'] = [kwargs['labels']]
            tempMS = [m for m in tempMS if set(m.labels).union(kwargs['labels'])]
            del kwargs['labels']
        for attr,val in kwargs.iteritems():
            if attr not in OPTIONAL_ATTRS + REQUIRED_ATTRS:
                raise Exception('%s is an unknown attribute of Message object' % attr)
            tempMS = [m for m in tempMS if m.__getattribute__(attr) == val]
            
        return tempMS
       
    def exclude(self,**kwargs):
        if kwargs.has_key('labels'):
            if isinstance(kwargs['labels'],str):
                 kwargs['labels'] = [kwargs['labels']]
            tempMS = [m for m in tempMS if not set(m.labels).union(kwargs['labels'])]
            del kwargs['labels']
        tempMS = MessageSet(self)
        for attr,val in kwargs.iteritems():
            if attr not in OPTIONAL_ATTRS + REQUIRED_ATTRS:
                raise Exception('%s is an unknown attribute of Message object' % attr)
            tempMS = [m for m in tempMS if m.__getattribute__(attr) != val]
            
        return tempMS
       
    def get(self,**kwargs):
        res = self.filter(kwargs)
        if len(res) != 1:
            raise Exception('More than one message matched using criteria: %s' % kwargs)
        return res[0]
        
    def unread(self):
        """Shortcut for MessageSet.filter(is_unread=True)."""
        return self.filter(is_unread=True)
