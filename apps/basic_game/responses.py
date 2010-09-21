from core.message import Message
from core.message_set import MessageSet
from apps.basic_game.models import *
from apps.basic_game.game_data import GAME, MESSAGES
from util.models import Log
import re


Team.objects.get_or_create(name="admin").save()
Team.objects.get_or_create(name="npc").save()

def join(message):
    team = message.text[len(GAME+"join"):].split()[0].lower()

    t = Team.objects(name=team)
    if not t:
        list_teams(message)

    else:
        print "%s is joining team %s" % (message.from_num, team)
        p = Phone.objects.get_or_create(number=message.from_num)
        p.team = team
        p.save()

        reply = Message(to_num = message.from_num, from_num = message.to_num, text = "The number %s has joined the game on team %s. To leave the game at any time text '%sleave' to %s." % (message.from_num, team, GAME, message.to_num))
    
        Log(message).save()
        Log(reply).save()
        message.connection.send(reply)

def list_teams(message):
    team_names = ", ".join([t.name for t in Team.objects(name__nin=["admin","npc"])])
    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "That wasn't a valid team. The following player teams are available: %s" % team_names)

    print "%s gave an invalid team" % message.from_num

    Log(message).save()
    Log(reply).save()
    message.connection.send(reply)


def already_joined(message):
    print "%s tried to join the game twice." % message.from_num

    p = Phone.objects.get(number=message.from_num)
    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "The number %s is already in the game on team %s. Wanna quit? Just text '%sleave' to %s." % (message.from_num, p.team, GAME, message.to_num))

    Log(message).save()
    Log(reply).save()
    message.connection.send(reply)

def leave(message):
    print "%s is leaving the game" % message.from_num

    p = Phone.objects.get(number=message.from_num)
    p.delete()

    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "The number %s has been taken out of the game. To join again, text '%sjoin TEAM' to %s." % (message.from_num, GAME, message.to_num))

    Log(message).save()
    Log(reply).save()
    message.connection.send(reply)

def not_joined(message):
    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "You are not in the game! To join, text '%sjoin TEAM' to %s." % (GAME, message.to_num))

    print "%s is not in the game yet, but sent a game message." % (message.from_num, message.text)

    Log(reply).save()
    Log(message).save()
    message.connection.send(reply)
    

def announce(message):

    sender = Phone.objects(number=message.from_num)
    if not sender:
        not_joined(message)
                
    else:
        phones = Phone.objects()
    
        text = message.text[len(GAME+"announce"):].strip()
        text = MESSAGES.get(text.lower(), text)
        #text = re.sub(r'announce', "admin:", message.text.lower().strip(), re.I)
        
        print "%s sending announcement \"%s\"" % (message.from_num, text)
        
        for phone in phones:
            tell = Message(to_num = phone.number, from_num = message.to_num, text = "To all: "+text)
            Log(tell).save()
            message.connection.send(tell)
    
        #reply = Message(to_num = message.from_num, from_num = message.to_num, text = "Your announcement has been sent.")
        #Log(reply).save()
        #message.connection.send(reply)
        Log(message).save()

def team_msg(message):
    team_name = message.text[len(GAME+"tell"):].split()[0].lower()
    
    sender = Phone.objects(number=message.from_num)
    if not sender:
        not_joined(message)
        
    elif team_name=="all":
        announce(message)
        
    elif not Team.objects(name=team_name):
        list_teams(message)
    
    else:
        phones = Phone.objects(team=team_name)
       
        text = re.sub(GAME+"tell (\w+)","", message.text, re.I).strip()
        text = MESSAGES.get(text.lower(), text)
        
        print "%s tells %s: %s" % (message.from_num, team_name, text)
        
        for phone in phones:
            tell = Message(to_num = phone.number, from_num = message.to_num, text = "Team %s: %s" % (team_name, text))
            Log(tell).save()
            message.connection.send(tell)
    
        reply = Message(to_num = message.from_num, from_num = message.to_num, text = "Your message has been sent to team %s." % team_name)
        Log(reply).save()
        Log(message).save()
        message.connection.send(reply)

#redefine available player teams
def set_teams(message):
    new_team_names = message.text[len(GAME+"set teams"):].split()
    old_teams = Team.objects(name__nin=["admin", "npc"])
    
    for team in old_teams:
        team.delete()
        for p in Phone.objects(team=team.name):
            p.delete()
    
    for team_name in new_team_names:
        Team(name=team_name).save()
        
    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "Old player teams deleted. New teams are %s." % ", ".join(new_team_names))

    Log(reply).save()
    Log(message).save()
    message.connection.send(reply)

#reset players and team scores (but not admin or available teams) 
def reset(message):
    teams = Team.objects(name__nin=["admin", "npc"])
    phones = Phone.objects(team__nin=["admin"])
    
    for team in teams:
        team.score = 0;
        team.save()
    
    for phone in phones:
        phone.delete()
        
    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "Scores and all non-admin players have been reset for all teams: %s" % ", ".join([t.name for t in teams]))

    Log(reply).save()
    Log(message).save()
    message.connection.send(reply)

#status
def status(message):
    scores = ", ".join(["%s: %d" % (t.name, t.score) for t in Team.objects(name__nin=["admin", "npc"])])
    
    #print "all participants: %s\nall teams:%s" % (", ".join(["%s on %s" % (p.number, p.team) for p in Phone.objects()]), ", ".join(["%s has %s points" % (t.name, t.score) for t in Team.objects()]))
    print "sending status to %s", message.from_num
    
    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "Current Scores: %s" % scores)

    Log(reply).save()
    Log(message).save()
    message.connection.send(reply)
    
#announce status to all
def announce_status(message, text):
    scores = ", ".join(["%s: %d" % (t.name, t.score) for t in Team.objects(name__nin=["admin", "npc"])])
    
    for phone in Phone.objects:
        announce = Message(to_num = phone.number, from_num = message.to_num, text = "%s\nCurrent Scores: %s" % (text, scores))
        Log(announce).save()
        message.connection.send(announce)
        
    Log(message).save()

def clear_scores(message):
    teams = Team.objects(name__nin=["admin", "npc"])
    
    for team in teams:
        team.score = 0;
        team.save()
        
    reply = Message(to_num = message.from_num, from_num = message.to_num, text = "Scores have been reset for teams %s. All participants are still in the game" % ", ".join([t.name for t in teams]))
    Log(reply).save()
    Log(message).save()
    message.connection.send(reply)
        

#score++ for team 
#(note to self: make sure the message gets saved in the Log
# either directly or by delegation (now in list_teams, announce_status))
def score(message):
    team_name = message.text[len(GAME+"score"):].split()[0].lower()
    
    teams = Team.objects(name=team_name)
    if not teams:
        list_teams(message)
    else:
        team = teams[0]
        team.score += 1
        team.save()
        print "%s was awarded a point by %s" % (team.name, message.from_num)
        announce_status(message, "Team %s has scored!" % team.name)
        
     
   