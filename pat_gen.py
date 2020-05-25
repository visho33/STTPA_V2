import itertools


def valid_homeaway_pattern(string): #introduces un patron de localia y te devuelve si es legal o no
  """
  :param string: string con patron de 1s y 0s
  :return: (bool) Indica si el patron es valido o no
  """
  local = string.count("0")
  visit = string.count("1")
  if local < 7 or visit < 7:
    return False
  if "111" in string or "000" in string:
    return False
  if string.count("00") > 1 or string.count("11") > 1:
    return False
  return True

def check_homeaway_pattern(team, home_match, full_patterns, teams, start_date): #
  """
  :param team: string alias equipo
  :home_match: Diccionario home_match[equipo][fecha]
  :full_patterns: Conjunto de patrones para 15 fechas
  :return: Conjunto de patrones que son posibles para
  el equipo
  """
  if start_date == 16 or start_date == 17:#Solo para fecha inicial 16 y 17
    correct_pat = list()
    for pattern in full_patterns:
      cond1 = pattern.count("1") == teams[team]['home_left'] # Localías faltantes
      if home_match[team][14] == 1 and home_match[team][15] == 1: # Ultimas dos fechas local,
        cond2 = pattern[0] == "0" # Primera fecha de la rueda visita.
      elif home_match[team][14] == 0 and home_match[team][15] == 0: # Ultimas dos fechas visita,
        cond2 = pattern[0] == "1" # Primera fecha de la rueda local.
      elif home_match[team][15] and pattern[0] == 1: # Break de local
        cond2 = pattern.count("11") == 0 # Ningún otro break
      elif home_match[team][15] == 0 and pattern[0] == 0: # Break de visita
        cond2 = pattern.count("00") == 0 # Ningún otro break
      else:
        cond2 = True
      if start_date == 17: #Solo si ya jugo fecha 16
        if home_match[team][16] == 1: #su fecha 16 debe coincidir con el patron
          cond3 = pattern[0] == "1"
        else:
          cond3 = pattern[0] == "0"
      else:
        cond3 = True
      if cond1 and cond2 and cond3:
        correct_pat.append(pattern)
    return correct_pat


  tent_correct_pat = list()
  pattern_start = ""
  for date in range(16, start_date): # Hacer calzar fechas jugadas
    pattern_start += str(home_match[team][date]) # con patron
  for pattern in full_patterns:
    if pattern[:start_date - 16] == pattern_start:
      tent_correct_pat.append(pattern)
  correct_pat = list()
  for pattern in tent_correct_pat: # Revisar si se llevo un break de rueda pasada
    if home_match[team][15] and pattern[0] == "1" and pattern.count("11") == 0:
      correct_pat.append(pattern)
    elif not home_match[team][15] and pattern[0] == "0" and pattern.count("00") == 0:
      correct_pat.append(pattern)
  return correct_pat

homeaway_patterns = filter(valid_homeaway_pattern, ["".join(seq) for seq in itertools.product("01", repeat=15)])
#Todos los posibles patrones pasados por la funcion de arriba
