import mongoengine as ME

ME.connect('weekender')

class Phone(ME.Document):
    number = ME.StringField(required=True)
    subscribed = ME.BooleanField(default=False)
    expert = ME.BooleanField(default=False)

    def __unicode__(self):
        return self.number

def main():
    surfer_count = Phone.objects(subscribed=True).count()
    expert_count = Phone.objects(expert=True).count()
    
    print "SurfAloud Status: %d surfers subscribed, %d experts registered." % (surfer_count, expert_count)
    
    print "Details: %s " % Phone.objects(subscribed=True)


if __name__ == "__main__":
    main()