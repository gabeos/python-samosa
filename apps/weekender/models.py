import mongoengine as ME

ME.connect('weekender')

class Phone(ME.Document):
    number = ME.StringField(required=True)
    subscribed = ME.BooleanField(default=False)
    expert = ME.BooleanField(default=False)

    def __unicode__(self):
        return self.number
