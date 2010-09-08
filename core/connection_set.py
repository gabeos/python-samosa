from core.message_set import MessageSet

class ConnectionSet(list):
  
    """Holds multiple connections in one contatiner and
    provides bulk access to common methods of its elements."""

    def get_messages(self):
        return MessageSet(m for conn in self for m in conn.get_messages())
        
