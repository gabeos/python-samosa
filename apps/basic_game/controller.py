from apps.basic_game.models import *
from util.models import Log
from apps.basic_game.responses import GAME
import apps.basic_game.responses
import re
from datetime import datetime


#define the app's behavior in the form of test / response pairs


#first define tests as functions that are given a Message object
#and perform arbitary evaluations, returning True or False
#(returning None is also evaluated as False)

#to prevent ghost messages if the server is restarted, ignore any messages that 
start_time = datetime.now().replace(second=0) 

def unread(message):
    return not Log.objects(m_id=message.id) and message.from_num != message.connection.num and message.datetime >= start_time

#anyone can join team admin or team npc, if they're evil.
def join_request(message):
    return message.text.lower().startswith(GAME+"join") and unread(message)

def is_joined(message):
    return bool(Phone.objects(number=message.from_num))

def join(message):
    return join_request(message) and unread(message) and not is_joined(message)

def already_joined(message):
    return join_request(message) and unread(message) and is_joined(message)

def leave(message):
    return message.text.lower().startswith(GAME+"leave") and (unread(message) and is_joined(message))

#currently, any player can send announcements or team messages.
#maybe only allow a player to send to their team? or not at all?
def announce(message):
    return message.text.lower().startswith(GAME+"announce") and unread(message)    

def team_msg(message):
    return message.text.lower().startswith(GAME+"tell") and unread(message)  

def score(message):
    return message.text.lower().startswith(GAME+"score") and unread(message) and (is_npc(message) or is_admin(message))

def reset(message):
    return message.text.lower().startswith(GAME+"reset") and unread(message) and is_admin(message)
    
def set_teams(message):
    return message.text.lower().startswith(GAME+"set teams") and unread(message) and is_admin(message)
    
def clear_scores(message):
    return message.text.lower().startswith(GAME+"clear") and unread(message) and is_admin(message)
    
def status(message):
    return message.text.lower().startswith(GAME+"status") and unread(message)

def is_admin(message):
    return bool(Phone.objects(number=message.from_num,team="admin"))

def is_npc(message):
    return bool(Phone.objects(number=message.from_num,team="npc"))

#Here associate tests with responses
reactions = (
                (join, apps.basic_game.responses.join),
                (already_joined, apps.basic_game.responses.already_joined),
                (leave, apps.basic_game.responses.leave),
                (announce, apps.basic_game.responses.announce),
                (team_msg, apps.basic_game.responses.team_msg),
                (score, apps.basic_game.responses.score),
                (set_teams, apps.basic_game.responses.set_teams),
                (reset, apps.basic_game.responses.reset),
                (status, apps.basic_game.responses.status),
                (clear_scores, apps.basic_game.responses.clear_scores)
            )
