class Config:
  MAX_CACHE_SIZE = 100 # items
  CACHE_TTL = 10800 # 3 hours (seconds)
  BASE_URL = 'https://www.anitube.vip'
  TITLE_EPISODE_PATTERN = r"(.+) ?-*.* ep +(\d+)"
  EPISODE_ID_PATTERN = r".+\/(\d+)"