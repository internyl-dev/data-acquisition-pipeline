
import logging
import datetime
import os

LOGS_DIR_PATH = "logs"

# Create datetime folder
time_now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

current_dir_path = f'{LOGS_DIR_PATH}/{time_now}'
os.mkdir(current_dir_path)

logger = logging.getLogger('Internyl')
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')

    # Debug file handler
    debug_file_handler=logging.FileHandler(f"{current_dir_path}/debug.txt")
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(formatter)

    # Warning file handler
    warning_file_handler=logging.FileHandler(f"{current_dir_path}/warnings.txt")
    warning_file_handler.setLevel(logging.WARNING)
    warning_file_handler.setFormatter(formatter)

    logger.addHandler(debug_file_handler)
    logger.addHandler(warning_file_handler)

# API log
api_log = open(f"{current_dir_path}/api_transaction.txt", 'a')