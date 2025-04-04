import logging
import traceback

logging.basicConfig(filename='error_log.txt', level=logging.ERROR, format='%(asctime)s [%(levelname)s]: %(message)s')

# deveria logar apenas erros, mas tá logando tudo kekw
def log_error(message, error):
  if error:
    filename, lineno, func, line = traceback.extract_tb(error.__traceback__)[-1]
    logging.error(f"{message}: {str(error)} Line: {lineno} Func: {func}, Code: {line} File: {filename}")
  else:
    logging.error(message)