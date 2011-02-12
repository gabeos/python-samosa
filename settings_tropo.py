#Specify connections here, format is (id,backend,[kwargs])
CONNECTIONS = (
                (
                    'Timmy the Tiny Talking Tropo',
                    'tropo',
                   {'TOKEN':'14b1c3f6aaf27b46aa008acb4e7c779bf2b986b194f2e1a1ffb160770c34a3af4dff141f42caec47489ff030',
                    'VOICE_TOKEN':'233e8641d2cb1a4d809731316b3d2448a7530e55fa3ad0a6787e097c28a0456049ba369623a4c3e0e66b7a6d'},
                ),
              )

#Set the interval to ping each connection for new Messages
#format is an integer in seconds, or a tuple specifying a range
#from which to wait a random number of seconds each time
CHECK_INTERVAL = (3, 3)

#Specify apps here, format is (app,[connection1,connection2...])
#if no connections are listed, all connections will be checked by default
APPS = (
            ('basic_game'), #('group_demo'),#('beowulf'),#('weekender'),#('joke'),
       )
