import pandas as pd
from pat_gen import homeaway_patterns, check_homeaway_pattern

#check_homeaway_pattern filtra los patrones validos para un equipo en concreto

def open_excel(name, page):
    """
    :param name: nombre del archivo a abrir
    :param page: nombre de la pagina de interes
    :return: lista por filas de pagina de excel
    """
    file = pd.ExcelFile(name)
    file = file.parse(page)
    column = []
    for key in file.keys():
        buff = []
        for i in range(len(file[key])):
            buff.append(str(file[key][i]).rstrip().replace("\xa0", " "))
        column.append(buff)
    buff = list(zip(*column))
    return buff

def parse_match(filename, start_date):
  """
  :param filename: nombre del archivo excel
  :return: {match: [{event_date: , home: , away: , winner: }]},
  {team: {date: home -> 1 else 0}}
  Retorna todos los 240 partidos del campeonato
  """
  match_file = open_excel(filename, 1)
  matches = {i: [] for i in range(1, 241)}
  date = False
  match = 240
  home_match = dict()
  teams_stats = dict()
  team_points = dict()
  for i in match_file:
    if i[0] != "nan":
      date = int(float(i[0]))
    else:
      _, home, away, score = i[1:5]
      score = [int(i.strip()) for i in score.split(":")]
      if score[0] > score[1]:
        winner = 'H'
      elif score[0] < score[1]:
        winner = "A"
      else:
        winner = "D"
      matches[match] = {"date": date, "home": home,
                        "away": away, "winner": winner}
      match -= 1
      if home not in team_points.keys():
        team_points[home] = 0
      if away not in team_points.keys():
        team_points[away] = 0
      if date < start_date:
        if winner == "H":
          team_points[home] += 3
        if winner == "A":
          team_points[away] += 3
        if winner == "D":
          team_points[home] += 1
          team_points[away] += 1

      if home not in home_match.keys():
        home_match[home] = dict()
      home_match[home][date] = 1
      if away not in home_match.keys():
        home_match[away] = dict()
      home_match[away][date] = 0

      if date >= start_date:
        if home not in teams_stats.keys():
          teams_stats[home] = {'wins': 0, 'loses': 0, 'draws': 0}
        if away not in teams_stats.keys():
          teams_stats[away] = {'wins': 0, 'loses': 0, 'draws': 0}
        if winner == "H":
          teams_stats[home]['wins'] += 1
          teams_stats[away]['loses'] += 1
        if winner == "A":
          teams_stats[away]['wins'] += 1
          teams_stats[home]['loses'] += 1
        if winner == "D":
          teams_stats[home]['draws'] += 1
          teams_stats[away]['draws'] += 1

  return matches, home_match, teams_stats, team_points

def parse_teams(filename):
  teams_file = open_excel(filename, 0)
  teams = {}
  for line in teams_file:
    _, _, alias, fr_points, home_left = line
    teams[alias] = {"fr_points": int(fr_points), "home_left": int(home_left)}
  return teams


#############################
#* PARAMETROS DE INSTANCIA *#
#############################
FECHAINI = 16
FECHAFIN = 24
FILENAME = "Datos"


# Carga de Datos
matches, home_match, teams_stats, team_points = parse_match(f"{FILENAME}.xlsx", FECHAINI)
teams = parse_teams(f"{FILENAME}.xlsx")



#################
#*  CONJUNTOS  *#
#################

# F: Fechas
F = list(range(FECHAINI, FECHAFIN + 1))

# I: Equipos
I = list(teams.keys())

# N: Partidos
N = list(range((FECHAINI - 1) * 8 + 1, FECHAFIN * 8 + 1))

# S: Patrones de localias
full_homeaway_patterns = list(homeaway_patterns).copy()
patterns = list(set([pat[FECHAINI - 16:FECHAFIN - 15] for pat in full_homeaway_patterns]))
patterns = {i + 1: patterns[i] for i in range(len(patterns))}
S = list(patterns.keys())

# T: Puntos
max_points = max([team_points[i] for i in I]) + 3 * (FECHAFIN + 2 - FECHAINI) #AQUI APLIQUE UN PARCHE
min_points = min([team_points[i] for i in I])
T = list(range(min_points, max_points + 1))

A = [0, 1, 3]


############################
#* PARAMETROS DEL MODELO *#
############################

# Eit: E[equipo][puntos]
# 1 si el equipo i tiene t puntos al iniciar
# 0 en otro caso
E = {i: {t: 1 if team_points[i] == t else 0 for t in T} for i in I}

# Rina: R[equipo][partido][puntos]:
# 1 si el equipo i gana a puntos en el partido n
#0 en otro caso

R = dict()
for i in I:
  R[i] = dict()
  for n in N:
    R[i][n] = dict()
    if i == matches[n]["home"]:
      if matches[n]["winner"] == "H":
        R[i][n][3] = 1
        R[i][n][1] = 0
        R[i][n][0] = 0
      elif matches[n]["winner"] == "D":
        R[i][n][1] = 1
        R[i][n][3] = 0
        R[i][n][0] = 0
      else:
        R[i][n][0] = 1
        R[i][n][1] = 0
        R[i][n][3] = 0
    elif i == matches[n]["away"]:
      if matches[n]["winner"] == "A":
        R[i][n][3] = 1
        R[i][n][1] = 0
        R[i][n][0] = 0
      elif matches[n]["winner"] == "D":
        R[i][n][1] = 1
        R[i][n][3] = 0
        R[i][n][0] = 0
      else:
        R[i][n][0] = 1
        R[i][n][1] = 0
        R[i][n][3] = 0
    else:
      R[i][n][0] = 0
      R[i][n][1] = 0
      R[i][n][3] = 0

# EL: EL[equipo][partido]
# 1 Si el equipo i es local en el partido n
# 0 En otro caso
EL = {i: {n: 1 if matches[n]['home'] == i else 0 for n in N} for i in I}

# EVin: EV[equipo][partido]
# 1 Si el equipo i es visita en el partido n
# 0 En otro caso
EV = {i: {n: 1 if matches[n]['away'] == i else 0 for n in N} for i in I}

# Wis: W[equipo][patron]
# 1 Si al equipo i se le puede asignar el
# patron de localias s
# 0 En otro caso
W = dict()
for team in teams.keys():
  W[team] = dict()
  possible_pat = check_homeaway_pattern(team, home_match, full_homeaway_patterns, teams, FECHAINI)
  possible_pat = list(set([pat[FECHAINI - 16:FECHAFIN - 15] for pat in possible_pat]))
  for pat_num in S:
    if patterns[pat_num] in possible_pat:
      W[team][pat_num] = 1
    else:
      W[team][pat_num] = 0

# Vf: V[fecha]
# Ponderación de atractivo de fecha f
V = {f: f - 15 for f in F}

# Lsf: L[patron][fecha]
# 1 Si el patron s indica que la fecha f
# es local
# 0 en otro caso
L = {s: {f: 1 if patterns[s][FECHAINI - f] == "1" else 0 for f in F} for s in S}

#Bitf: B[equipo][puntos][fecha]
#1 si el equipo i puede llegar a t puntos en la fecha f
#0 en otro caso

B = {i: {t: {f: 1 if t<=team_points[i] + 3*(f-FECHAINI+1) else 0 for f in F} for t in T} for i in I}


print("TERMINAMOS DE CARGAR PARAMETROS")