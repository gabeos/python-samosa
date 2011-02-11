from core.message import Message
from core.message_set import MessageSet
from apps.basic_game.models import *
from apps.basic_game.game_data import GAME, MESSAGES
from util.models import Log
import time
import re


Team.objects.get_or_create(name="admin").save()
Team.objects.get_or_create(name="npc").save()

def player_usage(message):
    Log(message).save()
    reply(message, "player commands:\n\
%sjoin TEAM\n\
%sleave TEAM\n\
%sstatus\n\
%stell TEAM MESSAGE\n\
%stell all MESSAGE" % (GAME, GAME, GAME, GAME, GAME))

def admin_usage(message):
    Log(message).save()
    reply(message, "help:\n\
%sjoin TEAM\n\
\" leave TEAM\n\
\" status\n\
\" tell TEAM MESSAGE\n\
\" tell all MESSAGE\n\
\" score TEAM [SCORE]\n\
\" clear scores\n\
\" reset teams\n\
\" set teams TEAM1 TEAM2..." % GAME)

def reply(original, text):
    reply = Message(to_num = original.from_num, from_num = original.to_num, text = text)

    Log(reply).save()
    original.connection.send(reply)

def join(message):
    team_match = re.match("(?i)"+GAME+"join (\w+)", message.text.lower())
    
    if not team_match or not Team.objects(name=team_match.group(1)):
        list_teams(message)
        return

    team = team_match.group(1)
    print "%s is joining team %s" % (message.from_num, team)
    p = Phone.objects.get_or_create(number=message.from_num)
    p.team = team
    p.save()

    Log(message).save()
    reply(message, "Your number %s has joined team '%s'. To leave the game at any time text '%sleave' to %s." % (message.from_num, team, GAME, message.to_num))
    #reply = Message(to_num = message.from_num, from_num = message.to_num, text = "The number %s has joined the game on team %s. To leave the game at any time text '%sleave' to %s." % (message.from_num, team, GAME, message.to_num))

    #Log(reply).save()
    #message.connection.send(reply)

def list_teams(message):
    print "%s gave an invalid team" % message.from_num
    Log(message).save()
    
    team_names = ", ".join([t.name for t in Team.objects(name__nin=["admin","npc"])])
    
    reply(message, "That wasn't a valid team. The following player teams are available: %s" % team_names)

def already_joined(message):
    print "%s tried to join the game twice." % message.from_num
    Log(message).save()
    
    p = Phone.objects.get(number=message.from_num)
    
    reply(message, "The number %s is already in the game on team %s. Wanna quit? Just text '%sleave' to %s." % (message.from_num, p.team, GAME, message.to_num))


def leave(message):
    print "%s is leaving the game" % message.from_num
    Log(message).save()
    
    p = Phone.objects.get(number=message.from_num)
    p.delete()

    reply(message, "The number %s has been taken out of the game. To join again, text '%sjoin TEAM' to %s." % (message.from_num, GAME, message.to_num))


def not_joined(message):
    Log(message).save()
    print "%s is not in the game yet, but sent a game message." % message.from_num
    
    reply(message, "You are not in the game! To join, text '%sjoin TEAM' to %s." % (GAME, message.to_num))



def announce(message):    
    text = message.text[len(GAME+"announce"):].strip()
    text = MESSAGES.get(text.lower(), text)
    #text = re.sub(r'announce', "admin:", message.text.lower().strip(), re.I)
    
    Log(message).save()
    print "%s sending announcement \"%s\"" % (message.from_num, text)
    
    announce_text(message, text)

    #reply = Message(to_num = message.from_num, from_num = message.to_num, text = "Your announcement has been sent.")
    #Log(reply).save()
    #message.connection.send(reply)

####IN PROGRESS#######
def team_msg(message):
    team_match = re.match("(?i)"+GAME+"tell (\w+)", message.text)
    text_match = re.match("(?i)"+GAME+"tell \w+ (.*)", message.text)
    
    if not team_match or not text_match:
        player_usage(message)
        return
        
    team_name = team_match.group(1)
    text = text_match.group(1)
        
    if team_name is "all":
        Log(message).save()
        announce_text(message, text)
        
    elif not Team.objects(name=team_name):
        list_teams(message)
    
    else:
        phones = Phone.objects(team=team_name)
        text = MESSAGES.get(text.lower(), text)
        Log(message).save()
        
        print "%s tells %s: %s" % (message.from_num, team_name, text)
        
        announce_text(message, "Team %s: %s" % (team_name, text), phones)
    
        if not Phone.objects(team=team_name, number=message.from_num):
            reply(message, "Your message has been sent to team %s." % team_name)

#redefine available player teams
def set_teams(message):
    new_team_names = message.text[len(GAME+"set teams"):].split()
    old_teams = Team.objects(name__nin=["admin", "npc"])
    
    Log(message).save()
    teams_string = ", ".join(new_team_names)
    print "setting teams to %s" % teams_string
    
    announce_text(message, "The game has been reset with new teams: %s. To join again, reply with '%sjoin TEAM'"%(teams_string), GAME)
    
    for team in old_teams:
        team.delete()
        for p in Phone.objects(team=team.name):
            p.delete()
    
    for team_name in new_team_names:
        Team(name=team_name).save()
        
    reply(message, "Old player teams deleted. New teams are %s." % ", ".join(new_team_names))


#reset players and team scores (but not admin or available teams) 
def reset(message):
    teams = Team.objects(name__nin=["admin", "npc"])
    phones = Phone.objects(team__nin=["admin"])
    Log(message).save()
    
    print "resetting all player scores and emptying all player teams..."
    
    announce_text(message, "The game has been reset. To rejoin the game, reply with '%sjoin TEAM'" % GAME)
    
    for team in teams:
        team.score = 0;
        team.save()
    
    for phone in phones:
        phone.delete()
        
    
    reply(message, "Scores and all non-admin players have been reset for all teams: %s" % ", ".join([t.name for t in teams]))


#status
def status(message):

    Log(message).save()
    print "sending status to %s" % message.from_num
    
    scores = ", ".join(["%s: %d" % (t.name, t.score) for t in Team.objects(name__nin=["admin", "npc"])])
    
    print "all participants: %s\nall teams:%s" % (", ".join(["%s on %s" % (p.number, p.team) for p in Phone.objects()]), ", ".join(["%s has %s points" % (t.name, t.score) for t in Team.objects()]))
    
    reply(message, "Current Scores: %s" % scores)

    
#announce status to all
def announce_text(message, text, phones=None):
    if phones is None:
        phones = Phone.objects
            
    for phone in phones:
        announce = Message(to_num = phone.number, from_num = message.to_num, text = text)
        Log(announce).save()
        message.connection.send(announce)
        time.sleep(1)  #if this fixes scaling issues, move it into connection.send()
        
def announce_status(message, text):
    scores = ", ".join(["%s: %d" % (t.name, t.score) for t in Team.objects(name__nin=["admin", "npc"])])
    announce_text(message, "%s\n%s" % (text, scores))
        
def clear_scores(message):
    teams = Team.objects(name__nin=["admin", "npc"])
    Log(message).save()  
    
    for team in teams:
        team.score = 0;
        team.save()
      
    announce_text(message, "Scores have been set to zero for all player teams. All participants are still in the game on their original teams.")
        

#score++ for team 
#(note to self: make sure the message gets saved in the Log
# either directly or by delegation (now in list_teams, announce_status))
def score(message):
    Log(message).save()
    team_name = re.sub("(?i)"+GAME+"score (\w+).*", r'\1', message.text, re.I).strip()
    teams = Team.objects(name=team_name)
    
    print message.text + ": " + team_name
    
    if not teams:
        list_teams(message)
        
    else:
        team = teams[0]
        score_match = re.match("(?i)"+GAME+"score "+team_name+" (\d+)", message.text)
        
        if score_match:
            score = int(score_match.group(1))
            team.score = score
            team.save()
            
            print "%s had their score set to %s by %s" % (team_name, score, message.from_num)
            
            reply(message, "Team %s has had their score set to %s" % (team_name, score))
            
        else:
            team.score += 1
            team.save()
            print "%s was awarded a point by %s" % (team.name, message.from_num)
            announce_status(message, "Team %s has scored!" % team.name)
            
        
     
   