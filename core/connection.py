import re

class FormatError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Connection(object):
 
    """Superclass for each backend's Connection object."""
  
    #add backend, number
    def __init__(self):
        pass

    def __repr__(self):
        return "<%s Connection for %s at %s>" % (self.backend, self.id, self.num)
        
    def len():
        return None
        
    def get_messages(self):
        raise NotImplementedError

    def send(self,msg):
        raise NotImplementedError
        
    def check_num_format(self,number):
        """Check if a number is in correct format:
        
        Numbers should be saved as strings, starting with +, followed by country code
        and then the number itself. No spaces."""
        
        format_re = re.compile(r'\+\d+')
        
        if not format_re.match(number):
            raise FormatError('Number should be: +[country-code][number]')
