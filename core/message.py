from datetime import datetime

REQUIRED_MSG_ATTRS = (
                #is id necessary if we're not saving the message somewhere?
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

        #should switch other defaults to this, and then just let them
        #be overwritten if passed as attrs
        self.labels = []
        
        for attr in REQUIRED_MSG_ATTRS:
            if not kwargs.has_key(attr):
                if attr == 'datetime':
                    self.datetime = datetime.now()
                    continue
                elif attr == 'id':
                    try:
                        self.id = kwargs['to_num'] + '_something' #fix this
                        continue
                    except KeyError:
                        raise Exception('%s is a required attribute of Message object' % attr)
                else:
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
        
    def send(self):
        """Shortcut method for msg.connection.send(msg).
        
        msg.connection attribute must be set."""
        try:
            self.connection.send(self)
        except AttributeError:
            raise AttributeError('Message must have connection attribute set.')
