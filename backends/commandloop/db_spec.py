import mongoengine as ME

ME.connect('')

class VirtualPhone(ME.Document):
    number = ME.StringField(required=True)
    messages = ME.ListField(EmbeddedDocument(VirtualMessage))


class VirtualMessage(ME.EmbeddedDocument):
    
    from_num = ME.StringField(required=True)
    to_num = ME.StringField(required=True)
    text = ME.StringField(required=True)
    datetime = ME.DateTimeField(required=True)
    labels = ME.ListField(ME.StringField(max_length=50))
    unread = ME.BooleanField(default=True)
      
        
