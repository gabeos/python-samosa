import mongoengine as ME

ME.connect('basic_game')

class Team(ME.Document):
    name = ME.StringField(unique=True)
    score = ME.IntField(default=0)
    def __unicode__(self):
        return self.name

class Phone(ME.Document):
    number = ME.StringField(required=True)
    team = ME.StringField()

    def __unicode__(self):
        return self.number

