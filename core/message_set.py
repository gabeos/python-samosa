

                
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
