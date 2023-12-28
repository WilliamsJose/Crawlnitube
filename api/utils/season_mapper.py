from api.utils.string_tools import normalize_string

def map_season(description_text):
  SEASON_MAP = {
    "SEGUNDA": 2,
    "TERCEIRA": 3,
    "QUARTA": 4,
    "QUINTA": 5,
    "SEXTA": 6,
    "SETIMA": 7,
    "OITAVA": 8,
    "NONA": 9,
    "DECIMA": 10,
    "UNDECIMA": 11,
    "DECIMA_PRIMEIRA": 11,
    "DUODECIMA": 12,
    "DECIMA_SEGUNDA": 12,
    "DECIMA_TERCEIRA": 13,
    "DECIMA_QUARTA": 14,
    "DECIMA_QUINTA": 15,
    "DECIMA_SEXTA": 16,
    "DECIMA_SETIMA": 17,
    "DECIMA_OITAVA": 18,
    "DECIMA_NONA": 19,
    "VIGESIMA": 20
  }
  
  first_word = normalize_string(str(description_text.split()[0]))
  second_word = normalize_string(str(description_text.split()[1]))
  
  if second_word == "TEMPORADA":
    return SEASON_MAP.get(first_word, 1)
  
  season_text = normalize_string(first_word + " " + second_word)
  return SEASON_MAP.get(season_text, 1)