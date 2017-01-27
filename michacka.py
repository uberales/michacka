# -*- coding: utf-8 -*-
"""
Takže... jak se nasadí optimální rozvržení týmů na Míchanou?

@author: Ales Podolnik
"""

import json
import codecs
import numpy
import copy
import random

# spocita statistiky jednoho tymu
# zadnej vodvaz, proste projede kazdyho s kazdym
def GetTeamStats(one_team):
    # statistiky obsahuji...
    # soucet strednich hodnot trueskillu
    mu = 0.0
    # soucet smerodatnych odchylek trueskillu
    sigma = 0.0
    # spolecne ucasti hracu s ostatnimi v tymu
    common_participations = []
    # celkovy pocet dvojic v tymu, ktere spolu uz nekdy sly
    pair_count = 0
    
    for player_a in one_team:
        # sigmy a mu proste sectem
        mu += player_a['mu']
        sigma += player_a['sigma']
        
        cp_count = 0;
        # zjistime, kolikrat hrac uz nekdy sel s nekym z ostatnich
        for player_b in one_team:
            # sam onen hrac nas nezajima
            if player_b["id"] != player_a["id"]:
                partners = player_a['partners']
                # id je jako string v odpovidajicim dictionary
                str_id = str(player_b["id"])
                # je potreba otestovat, jestli spolu vubec sli
                cp = (partners[str_id] if str_id in partners else 0)
                # pricti ke spolecnym ucastem a zapocitej do spolecnych paru
                cp_count += cp
                pair_count += (1 if cp > 0 else 0)
    
        # pridej spolecne ucasti hrace do celkovych statistik tymu
        common_participations.append(cp_count)
    
    # aby byla statkova metodika zachovana, melo by se neco malo pricist k sigme, ale...
    
    team_stats = {
        "mu": mu,
        "sigma": sigma,
        "common_participations": common_participations, 
        "pair_count": pair_count / 2 # vydelime dvema, pac se to zapocitavavalo dvakrat
    }

    return team_stats;

# ohodnot, jak dobre jsou seskladane vsechny tymy
def ScoreDistribution(all_teams):
    stats = [GetTeamStats(t) for t in all_teams]
    return GetFitness(stats)

# spocitej fitness funkci
def GetFitness(all_scores):
    # rozdeleni tymu je dobry
    # - pokud maji trueskilly tymu co nejmensi smerodatnou odchylku
    # - pokud je v tymech co nejnizsi pocet dvojic, co spolu uz sly
    # tady by se daly dopsat dalsi statisticky zjistitelny podminky
    # napr. jak vymyslet distribuci zen v tymech, ale to jsem nakonec vyresil jinak

    fitness = {
        "std": numpy.std([s['mu'] for s in all_scores]),
        "sum": numpy.sum([s['pair_count'] for s in all_scores])
    }
    return fitness

# srovnej fitness dvou tymu
def CompareFitness(fitness_a, fitness_b):
    
    diff_sum = fitness_a["sum"] - fitness_b["sum"]
    diff_std = fitness_a["std"] - fitness_b["std"]
    
    # fitness prvniho tymu (A) je lepsi, pokud ma nizsi oba parametry (nebo pri rovnosti jednoho z nich, ten druhej)
    
    if diff_sum < 0 and diff_std < 0:
        return -1
    elif diff_std == 0:
        return diff_sum
    elif diff_sum == 0:
        return diff_std
    else:
        return 1

# prohod dva nahodne hrace ve dvou nahodnych tymech
# vstup: hraci, max pocet zen
def SwapPlayers(all_teams, max_women):
    new_teams = []
    
    # budeme prochazet tak dlouho, dokud vygenerovane tymy nebudou splnovat podminku na max pocet zen v tymu
    while True:
        # jsem prase a nechce se mi resit nejaky hlidani, co se stane s objektama, tak to proste zkopiruju, v tomhle pouziti je to fuk
        new_teams = copy.deepcopy(all_teams)
        
        # vyberu nahodny dva tymy
        team_a = new_teams[random.randint(0, len(new_teams) - 1)]
        team_b = new_teams[random.randint(0, len(new_teams) - 1)]
        
        # v nech nahodny dve pozice
        # bacha - prvni clen (zena) je fixni
        # timhle se hlida, ze v kazdym tymu je aspon jedna zena (teda pokud je zen dostatek, jinak to proste fixuje prvniho clena, coz neva)
        index_a = random.randint(1, len(team_a) - 1)
        index_b = random.randint(1, len(team_b) - 1)
        
        # prohodi hrace
        player_a = team_a.pop(index_a)
        team_b.append(player_a)
        player_b = team_b.pop(index_b)        
        team_a.append(player_b)
        
        # otestuje podminku na max pocet zen v tymu
        if CountWomen(team_a) <= max_women and CountWomen(team_b) <= max_women:
            break
        else:
            # kdyby nahodou byly prohazovany tymy s limitnim poctem zen, tak si pockame, dokud nebudou prohozeny zeny (lazy...)
            print 'Too many women per randomized team, trying again.'
    
    # jestli jsme se nezacyklili, tak hotovo. k zacykleni by snad dojit nemelo
    return new_teams

# obal pro pocitani zen
def CountWomen(team):
    w = numpy.sum([p["woman"] for p in team])
    return w

# nastrel pocatecni rozlozeni lidi v tymu
# nahaze lidi do tymu v sirce, nejdriv zeny, zbytek chlapi
# pri mensim poctu lidi nez by pokrylo vsechny tymy ekvivalentne, by to melo generovat tymu s jednim hracem navic/min (podle toho, jaky je team_count) nez jeden znevyhodneny a ostatni akorat
def GenerateTeamSeed(men, women, team_count, max_members):
    
    # pomichame kandidaty
    random.shuffle(women)
    random.shuffle(men)

    # vytvorime prazdny tymy
    teams = [[] for i in range(team_count)]
    
    # naplnime je lidma, nejdriv zeny
    i = 0
    for p in women:
        team = teams[i % team_count]
        team.append(p)
        i += 1
    # pak muzi, pricemz postupne iterujeme mezi tymama
    for p in men:
        team = teams[i % team_count]
        team.append(p)
        i += 1    
    
    return teams

# nastaveni hry
max_members = 4

# nacteme ucastniky (musime predem spustit michana_parser.py, ktery je postahuje ze Statku)
participants = [];
with codecs.open('data/michana_participants.json', 'r', encoding='utf8') as f:
    participants = json.loads(f.read())

# filtrujeme pohlavi
women = [p for p in participants if p["woman"]]
men = [p for p in participants if not(p["woman"])]

# nastavime pocet tymu
# floor nebo ceil v team_count urci vysledne vyvazeni v pripade nerovnosti tymu
team_count = int(numpy.ceil(len(participants) / max_members))
# aspon nejaky zeny, ale ne moc
max_women = int(numpy.ceil(1.0 * len(women) / team_count))

# inicializujeme zaznamy pro kandidaty
candidates = []

# kolikrat chceme nastrelit tym a kolikrat ho chceme nechat relaxovat
# iteraci musi byt radove 1000, aby se dosahlo rozumnyho minima
seed_count = 1000
iteration_count = 1000

for i in range(seed_count):
    # nastrelime nejake rozdeleni tymu a spocitame jeho fitness
    teams = GenerateTeamSeed(men, women, team_count, max_members)
    fitness = ScoreDistribution(teams)
    
    for j in range(iteration_count):
        # zkusime neco zmenit nahodnym prehozenim dvou hracu
        new_teams = SwapPlayers(teams, max_women)
        new_fitness = ScoreDistribution(new_teams)
        
        # podivame se, jestli jsme neco zlepsili
        if CompareFitness(new_fitness, fitness) < 0:
            # jestli jo, tak si to schovame
            teams = new_teams
            fitness = new_fitness
    
    # prosli jsme iterace, nasli jsme kandidata    
    candidate = {"fitness": fitness, "teams": teams}
    candidates.append(candidate)
    # podivame se na jeho fitness
    print str(i) + ": " + str(candidate["fitness"])

# seradime kandidaty - preferujeme ty, kteri maji co nejnizsi pocet spolecnych ucasti dvojic
candidates = sorted(candidates, key = lambda c: (c["fitness"]["sum"], c["fitness"]["std"]))

# trochu to preparsujeme, at se to da ve vystupu cist
readable_teams = []
best_teams = candidates[0]["teams"]    
readable_teams = [
    {"mu": stats["mu"], "sigma": stats["sigma"], "names": [p["name"] for p in team]} 
    for team, stats in zip(best_teams, [GetTeamStats(t) for t in best_teams])
]

# tohle je vysledek
final_distribution = {"fitness": candidates[0]["fitness"], "teams": readable_teams}
print final_distribution

# zapiseme ho nekam...
with codecs.open('data/michana_distribution.json', 'w', encoding='utf8') as f:
    data = json.dumps(final_distribution, ensure_ascii = False, indent=4, separators=(',', ': '))
    f.write(data)
