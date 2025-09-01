
import logging
import datetime
import os
import sys
from pprint import pp

from .base_observer import Observer

class Observable:
    def __init__(self):
        self.observers = []
    
    def register(self, *args:Observer):
        for observer in args:
            self.observers.append(observer)

    def update(self, *args, level=None):
        for observer in self.observers:
            observer.update(*args, level=level)

class Logger(Observer):
    def __init__(self, log_mode):

        self.LOGS_DIR_PATH = "logs"

        self.log_mode = log_mode

        self.logger = logging.getLogger('Internyl')
        self.logger.setLevel(logging.DEBUG)

    def create_logging_files(self):
        """
        Sets up the logging files if log mode was turned on when setting up the instance.
        """
        if not self.log_mode:
            return
        
        if os.path.isdir(self.LOGS_DIR_PATH):
            self.logger.info(f"Path '{self.LOGS_DIR_PATH}' does not exist. Attempting to create directory...")
        
        try:
            os.makedirs(self.LOGS_DIR_PATH, exist_ok=True)
            self.logger.info(f"Either path '{self.LOGS_DIR_PATH} exists or it was created.\n"
                             "Either way this message indicates that the logging system is functional thusfar.")
        except OSError as e:
            self.logger.critical(f"Error creating directory '{self.LOGS_DIR_PATH}': {e}\nExiting program...")
            sys.exit()

        # Create datetime folder
        time_now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        current_dir_path = f'{self.LOGS_DIR_PATH}/{time_now}'
        os.mkdir(current_dir_path)

        if not self.logger.handlers:
            formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')

            # Debug file handler
            debug_file_handler=logging.FileHandler(f"{current_dir_path}/debug.txt")
            debug_file_handler.setLevel(logging.DEBUG)
            debug_file_handler.setFormatter(formatter)

            # Warning file handler
            warning_file_handler=logging.FileHandler(f"{current_dir_path}/warnings.txt")
            warning_file_handler.setLevel(logging.WARNING)
            warning_file_handler.setFormatter(formatter)

            self.logger.addHandler(debug_file_handler)
            self.logger.addHandler(warning_file_handler)

        # API Log
        self.api_log = open(f"{current_dir_path}/api_transaction.txt", 'a')


    def apply_conditional_logging(self):
        """
        Creates and applies a wrapper to every single `logging` method to write the output into a logging file
        and `pp` the message into the terminal.
        """
        if not hasattr(self, 'logger'):
            return
            
        def __log_mode_guard(func):
            def wrapper(*args, **kwargs):
                if not self.log_mode:
                    return
                
                if kwargs.get("message", False):
                    message = kwargs["message"]
                
                if args:
                    message = args[0]

                func(message)
                pp(message)
                return
                
            return wrapper

        self.logger.debug = __log_mode_guard(self.logger.debug)
        self.logger.info = __log_mode_guard(self.logger.info)
        self.logger.warning = __log_mode_guard(self.logger.warning)
        self.logger.error = __log_mode_guard(self.logger.error)
        self.logger.critical = __log_mode_guard(self.logger.critical)

    def update(self, *args, level=None):
        def __iterlog(method):
            for msg in args:
                method(msg)

        if not level:
            __iterlog(self.logger.info)
        elif level==logging.DEBUG:
            __iterlog(self.logger.debug)
        elif level==logging.INFO:
            __iterlog(self.logger.info)
        elif level==logging.WARNING:
            __iterlog(self.logger.warning)
        elif level==logging.ERROR:
            __iterlog(self.logger.error)
        elif level==logging.CRITICAL:
            __iterlog(self.logger.critical)