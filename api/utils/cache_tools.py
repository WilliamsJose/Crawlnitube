from cachetools import TTLCache
from config.config import Config

cache = TTLCache(Config.MAX_CACHE_SIZE, Config.CACHE_TTL)

def has_cached(cache_key):
  if cache_key in cache:
    return cache[cache_key]
  else:
    return None
  
def save_in_cache(cache_key, data):
  cache[cache_key] = data