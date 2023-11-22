from api.utils.logger import log_error

def time_to_minutes(time_str):
  parts = time_str.split(':')
  total_minutes = None
  if len(parts) == 3:
    hours, minutes, seconds = map(int, parts)
    total_minutes = hours * 60 + minutes + seconds / 60
  elif len(parts) == 2:
    minutes, seconds = map(int, parts)
    total_minutes = minutes + seconds / 60
  else:
    log_error(f"time_to_minutes: Invalid time format: {time_str}")

  return round(total_minutes, 0)
