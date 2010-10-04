#Specify connections here, format is (id,backend,[kwargs])
CONNECTIONS = (
                 (
                    'doctor.hrothgar@gmail',
                    'pygooglevoice',
                    {'GV_USER':"doctor.hrothgar@gmail.com",'GV_PASSWORD':None}
                 ),
              )

#Set the interval to ping each connection for new Messages
#format is an integer in seconds, or a tuple specifying a range
#from which to wait a random number of seconds each time
CHECK_INTERVAL = (60, 120)

#Specify apps here, format is (app,[connection1,connection2...])
#if no connections are listed, all connections will be checked by default
APPS = (
            ('weekender'),
       )
