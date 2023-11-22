import logging
import traceback

logging.basicConfig(filename='error_log.txt', level=logging.ERROR, format='%(asctime)s [%(levelname)s]: %(message)s')

def log_error(message, error):
  if error:
    filename, lineno, func, line = traceback.extract_tb(error.__traceback__)[-1]
    logging.error(f"{message}: \nFile: {filename}, Line: {lineno}, Func: {func}, Code: {line}")
  else:
    logging.error(message)