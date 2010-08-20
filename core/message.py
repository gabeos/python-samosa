

REQUIRED_MSG_ATTRS = (
                'id',
                'datetime',
                'from_num', #optional??
                'to_num',
                'text'
                 )
    
OPTIONAL_MSG_ATTRS = (
                'labels',
                'is_read',
                'connection'
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
    
    def __cmp__(self, other):
        return cmp(self.datetime, other.datetime)
            