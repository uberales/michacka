# -*- coding: utf-8 -*-
"""
@author: Ales Podolnik
"""

import re
import codecs
from statek import StatekSlave
import json
import getpass

# a simple method how to match females (surname ending with -ova or -ska)
def IsWoman(name):
    stripped_name = name.replace(u'á', 'a')
    if re.match('.*ova$', stripped_name):
        return True
    if re.match('.*ska$', stripped_name):
        return True
    if re.match(u'.*lá$', name):
        return True
    if re.match(u'.*chá$', name):
        return True
    return False

# a shortcut for creating player's record
def CreatePlayer(player_id, name, sigma, mu):
    player = {
        "id": int(player_id), 
        "name": name, 
        "sigma": float(sigma.replace(",", ".")), 
        "mu": float(mu.replace(",", ".")),
        "partners": {}, 
        "woman": IsWoman(name)
    }
    return player

# get login data from user
login = raw_input("Statek login: ")
password = getpass.getpass("Statek password: ")

# create an instance of Statek slave
otrok = StatekSlave(login, password)
# if the login is unsuccessful, parsing will fail for matched players, but whatever...

# load page with wagers
data_str = otrok.Get('michana-2017/nasazeni')

# try to find matched players first
pattern = r'<tr.+? class="members"><a title=.+?href.+?hraci\/([0-9]*)">(.+?)<\/a>.+?"mu">([-0-9,]*)<\/td>.+?"sigma">([0-9,]*)<\/td><\/tr>'
matches = re.findall(pattern, data_str)

# create matched players from loaded data
matched_players = [CreatePlayer(m[0], m[1], m[3], m[2]) for m in matches]

# we'll need this for filtering
participant_ids = set([p["id"] for p in matched_players])

# matched players done
print 'Parsed matched players from Statek'

# unmatched players have slightly different syntax
pattern = r'<tr class=""><td title.+?"expected_rank".+?"name".+?"members"><span.+?>(.+?)<\/span>.+?"mu">([-0-9,]*)<\/td>.+?"sigma">([0-9,]*)<\/td><\/tr>'
matches = re.findall(pattern, data_str)

# unmatched partners do not have an id in Statek
unmatched_players = [CreatePlayer("0", m[0], m[2], m[1]) for m in matches]
print 'Parsed unmatched players from Statek'


# let's go through matched players and find whomever they have played with
# filter it with respect to current participants
for player in matched_players:
    # slave will get an JSON record for each player
    player_json = otrok.Get('hraci/' + str(player['id']) + '.json')
    player_record = json.loads(player_json)
    
    # find teammates and filter them
    partners = [f["id"] for f in player_record["friends"] if f["id"] != player["id"]]
    partners = list(set(partners).intersection(participant_ids))
    
    # find common participation occurences for all partners
    common_participations = [(cm["count"] for cm in player_record["common_membership"] if cm["user_id"] == player["id"] and cm["partner_id"] == p_id).next() for p_id in partners]

    # pack it together
    player['partners'] = dict(zip(partners, common_participations));    
    # assume gender (TRIGGERED!)
    
    # done
    print "Player loaded: " + player["name"]

# concatenate with unmatched players
participants = matched_players + unmatched_players

# store results as JSON
with codecs.open('data/michana_participants.json', 'w', encoding='utf8') as f:
    data = json.dumps(participants, ensure_ascii = False, indent=4, separators=(',', ': '))
    f.write(data)
