from core.message_set import MessageSet
from core.connection import Connection as SuperConn
from getpass import getpass

class Connection(SuperConn):
    """Manages multiple connections invisibly"""
    
    def get_messages(self):
        """Retrieve messages from all connections and return MessageSet instance"""
        
        print("(multi) checking all connections")
        
        msg_list = [];
        for cid, backend, creds in self.connection_data:
            conn = self.make_connection(cid, backend, creds)
            for m in conn.get_messages():
                m.connection = self #replies will use our active sender.
                msg_list.append(m)
                
        #use a different sender connection after every check cycle. 
        #Alternatively, we could decide based on time or sent-message count.
        #otherwise, the last connection that was made will be used for sending.
        self.activate_next_connection()
        return MessageSet(msg_list)  
        
    #make a new connection with the given information.
    #update active_connection so it's always valid.
    def make_connection(self, cid, backend, creds):
         
         print "(multi) connecting to %s" % cid
         c = __import__('backends.%s' %backend,globals(),locals(),['connection'],-1)
         self.active_connection = c.connection.Connection(cid,**creds)
         self.num = self.active_connection.num
         return self.active_connection
        
    def activate_next_connection(self):
        """for load-balancing, use this occasionally to switch up the sender"""
        print("(multi) setting the active sender connection...")
        
        cid = self.connection_data[self.next_conn][0]
        backend = self.connection_data[self.next_conn][1]
        creds = self. connection_data[self.next_conn][2] 
         
        self.make_connection(cid, backend, creds)
        
        #next time, it's somebody else's turn.
        self.next_conn = (self.next_conn + 1) % len(self.connection_data)
        
    def send(self,message):
        """Send a message using an arbitrary connection from our collection."""
        self.active_connection.send(message)
    
    def __repr__(self):
        return "<Multi Connection '%s' at %s>" % (self.id, [data[0] for data in self.connection_data])
        
    def __init__(self, cid, **kwargs):
        """A Connection Combo! Each connection will be created each time it's needed."""
    
        #self.num = '+1111111111' #get the num from the active connection
        self.id = cid
        self.backend = 'multiplex'
        
        self.next_conn = 0
        self.connection_data = kwargs['connection_data']
        
        #fudgy GV hack for remembering passwords. 
        for cid, backend, kwargs in self.connection_data:
            if backend is 'pygooglevoice':
                if kwargs['GV_USER'] is None:
                    kwargs['GV_USER'] = raw_input("Username for %s:" % cid)
                if kwargs['GV_PASSWORD'] is None:
                    kwargs['GV_PASSWORD'] = getpass("Password for %s:" % cid)
        
        print "starting multi connection '%s' for %s" % (self.id, [cid for cid, backend, args in self.connection_data])
        self.activate_next_connection()
        
