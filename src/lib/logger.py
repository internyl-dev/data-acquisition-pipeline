
import logging
import datetime
import os

class Logger:
    def __init__(self, log_mode):

        self.LOGS_DIR_PATH = "logs"

        self.log_mode = log_mode

        self.logger = logging.getLogger('Internyl')
        self.logger.setLevel(logging.DEBUG)

    def create_logging_files(self):
        if not self.log_mode:
            return

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
        if not hasattr(self, 'logger'):
            return
            
        def log_mode_guard(func):
            def wrapper(*args, **kwargs):
                if not self.log_mode:
                    return
                
                if kwargs.get("message", False):
                    func(kwargs["message"])
                    return
                
                if args:
                    func(args[0])
                    return
            return wrapper

        self.logger.debug = log_mode_guard(self.logger.debug)
        self.logger.info = log_mode_guard(self.logger.info)
        self.logger.warning = log_mode_guard(self.logger.warning)
        self.logger.error = log_mode_guard(self.logger.error)
        self.logger.critical = log_mode_guard(self.logger.critical)

    def setup_logging_main(self):
        self.create_logging_files()
        self.apply_conditional_logging()