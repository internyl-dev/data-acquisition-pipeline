
import logging
import datetime
import os
from pprint import pprint, pformat

from .base_observer import Observer

class Observable:
    def __init__(self) -> None:
        self.observers = []
    
    def register(self, *args:Observer) -> None:
        for observer in args:
            self.observers.append(observer)

    def update(self, *args, level=None) -> None:
        for observer in self.observers:
            observer.update(*args, level=level)

class Logger(Observer):
    def __init__(self, enabled:bool = True, level=logging.INFO) -> None:
        self._enabled = enabled

        self.LOGS_DIR_PATH = "logs"
        time_now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.CURRENT_DIR_PATH = f"{self.LOGS_DIR_PATH}/{time_now}"

        self.logger = logging.getLogger(__name__)
        self.api_logger = logging.getLogger("__api_transaction__")
        self.setup(level)

    def setup(self, level) -> None:
        """
        Sets up in the specified order:
        1. Basic configurations
        2. File setup/creation
        3. File handlers
        """
        print("setting up...")
        logging.basicConfig(level=level)
        self._setup_files()

        debug_file_handler = logging.FileHandler(f"{self.CURRENT_DIR_PATH}/debug.txt")
        debug_file_handler.setLevel(logging.DEBUG)
        warning_file_handler = logging.FileHandler(f"{self.CURRENT_DIR_PATH}/warnings.txt")
        warning_file_handler.setLevel(logging.WARNING)
        info_file_handler = logging.FileHandler(f"{self.CURRENT_DIR_PATH}/info.txt")
        info_file_handler.setLevel(logging.INFO)
        api_log_handler = logging.FileHandler(f"{self.CURRENT_DIR_PATH}/api_log.txt")
        api_log_handler.setLevel(logging.NOTSET)

        formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
        api_formatter = logging.Formatter("[%(asctime)s]: %(message)s")

        debug_file_handler.setFormatter(formatter)
        warning_file_handler.setFormatter(formatter)
        info_file_handler.setFormatter(formatter)
        api_log_handler.setFormatter(api_formatter)

        self.logger.addHandler(debug_file_handler)
        self.logger.addHandler(warning_file_handler)
        self.logger.addHandler(info_file_handler)
        self.api_logger.addHandler(api_log_handler)

    def _setup_files(self) -> None:
        os.makedirs(self.CURRENT_DIR_PATH, exist_ok=True)

    def toggle(self) -> bool:
        self._enabled = not self._enabled
        if self._enabled: self._setup_files()
        return self._enabled

    def enable(self) -> None:
        self._enabled = True
        self._setup_files()
    
    def disable(self) -> None:
        self._enabled = False

    @staticmethod
    def __iterlog(method, *args) -> None:
        for msg in args:
            method(msg)
            pprint(msg)

    def update(self, *args, level=None) -> None:
        if not self._enabled:
            return

        print("doing thing")
            
        match level:
            case logging.DEBUG:
                self.__iterlog(self.logger.debug, *args)
            case logging.INFO:
                self.__iterlog(self.logger.info, *args)
            case logging.WARNING:
                self.__iterlog(self.logger.warning, *args)
            case logging.ERROR:
                self.__iterlog(self.logger.error, *args)
            case logging.CRITICAL:
                self.__iterlog(self.logger.critical, *args)
            case _:
                self.__iterlog(self.logger.info, *args)  # fallback
                print("falling back twin")

    def update_api(self, d: dict) -> None:
        self.api_logger.info(pformat(d))

if __name__ == "__main__":
    log = Logger()
    log.update("test")

    test_dict = test_data = {
    "users": [
            {"id": 1, "name": "Alice", "roles": ["admin", "editor"], "active": True},
            {"id": 2, "name": "Bob", "roles": ["viewer"], "active": False},
            {"id": 3, "name": "Charlie", "roles": ["editor", "viewer"], "active": True},
        ],
        "settings": {
            "theme": "dark",
            "notifications": {"email": True, "sms": False, "push": True},
            "languages": ["en", "fr", "es"],
        },
        "projects": {
            "project1": {
                "name": "Apollo",
                "status": "active",
                "tasks": [
                    {"task_id": 101, "title": "Design UI", "completed": False},
                    {"task_id": 102, "title": "Setup backend", "completed": True},
                ],
            },
            "project2": {
                "name": "Zeus",
                "status": "completed",
                "tasks": [
                    {"task_id": 201, "title": "Research", "completed": True},
                    {"task_id": 202, "title": "Prototype", "completed": True},
                ],
            },
        },
        "metadata": {
            "created_at": "2025-12-28T13:00:00",
            "updated_at": "2025-12-28T14:30:00",
            "tags": ["urgent", "high-priority", "client-facing"],
        },
        "logs": [
            {"level": "INFO", "message": "System started", "timestamp": "2025-12-28T13:01:00"},
            {"level": "WARNING", "message": "Low disk space", "timestamp": "2025-12-28T13:15:00"},
            {"level": "ERROR", "message": "Failed to connect to DB", "timestamp": "2025-12-28T13:45:00"},
        ],
    }

    log.update_api(test_dict)