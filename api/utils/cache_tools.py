from cachetools import TTLCache
from config.config import Config
import logging

cache = TTLCache(Config.MAX_CACHE_SIZE, Config.CACHE_TTL)

def has_cached(cache_key):
  try:
    if cache_key in cache:
      return cache[cache_key]
  except Exception as e:
    logging.error(f"has_cached: Unexpected error: {e}")
  return None

  
def save_in_cache(cache_key, data):
  try:
    cache[cache_key] = data
  except Exception as e:
    logging.error(f"save_in_cache: Unexpected error: {e}")