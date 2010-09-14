class Controller(object):

    """a Controller instance is initialized with the names of the apps
    which it manages using its control() method, which takes a message
    set and runs each apps tests on each message on the set, performing
    the app's response if the test returns true."""

    def __init__(self,app_names):
        """Instantiate a controller.
        
        Argument:
        app_names -- the names of apps to manage (corresponding to dirs in the apps subdir)
        """

        self.reactions = tuple()
        for app_name in app_names:
            a = __import__('apps.%s' % app_name,globals(),locals(),['controller'],-1)
            self.reactions += a.controller.reactions
        self.app_names = app_names

    def control(self,msg_set):
        """Run all apps' tests on each message, call associated response if test passes.
        
        Arguments:
        msg_set -- the set of messages to test"""

        for msg in msg_set:
            for test, response in self.reactions:
                if test(msg):
                    response(msg)
