#Specify connections here, format is (id,backend,[kwargs])
CONNECTIONS = (
                 (
                    'GV combo',
                    'multiplex',
                    {'connection_data':
                        ((
                            'doctor.hrothgar@gmail',
                            'pygooglevoice',    
                            {'GV_USER':"doctor.hrothgar@gmail.com",'GV_PASSWORD':None},
                        ),
                        (
                            'askory@andrew',
                            'pygooglevoice',    
                            {'GV_USER':"askory@andrew.cmu.edu",'GV_PASSWORD':None},
                        ))
                    },
                  ),
              )

#Set the interval to ping each connection for new Messages
#format is an integer in seconds, or a tuple specifying a range
#from which to wait a random number of seconds each time
CHECK_INTERVAL = (30, 90)

#Specify apps here, format is (app,[connection1,connection2...])
#if no connections are listed, all connections will be checked by default
APPS = (
            ('weekender'),
       )
