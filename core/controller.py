

class Controller(object):

    def __init__(self,app_names):

        self.reactions = tuple()
        for app_name in app_names:
            a = __import__('apps.%s' % app_name,globals(),locals(),['controller'],-1)
            self.reactions += a.controller.reactions

    def control(self,msg_set):
        for msg in msg_set:
            for test, response in self.reactions:
                if test(msg):
                    response(msg)
