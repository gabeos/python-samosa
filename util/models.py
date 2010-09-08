import mongoengine as ME

class Log(ME.Document):
    to_num = ME.StringField(required=True)
    from_num = ME.StringField(required=True)
    text = ME.StringField(required=True)
    datetime = ME.DateTimeField(required=True)
    labels = ME.ListField(StringField(max_length=50)

    def __init__(self,msg=None,**kwargs):
        """Allow initialization with message object as single argument"""

        if msg:
            super(Log,self).__init__(
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

