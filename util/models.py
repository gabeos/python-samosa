import mongoengine as ME

class Log(ME.Document):
    m_id = ME.StringField() #not required because Mongo creates its own unique ids
                            #this corresponds to message ids that an cxn/app might create
    to_num = ME.StringField(required=True)
    from_num = ME.StringField(required=True)
    text = ME.StringField(required=True)
    datetime = ME.DateTimeField(required=True)
    labels = ME.ListField(ME.StringField(max_length=50))

    def __init__(self,msg=None,**kwargs):
        """Allow initialization with message object as single argument"""

        if msg:

            try:
                m_id = msg.id
            except AttributeError:
                m_id = None

            super(Log,self).__init__(
                m_id = m_id,
                to_num=msg.to_num,
                from_num=msg.from_num,
                text=msg.text,
                datetime=msg.datetime,
                labels=msg.labels
            )
        else:
            super(Log,self).__init__(**kwargs)

    def __repr__(self):
        return "<Message from %s to %s>" % (self.from_num, self.to_num)
