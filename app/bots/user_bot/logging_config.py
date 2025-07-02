import logging
import os


class Logger:
    '''Класс для логирования
        При создание объекта передать имя файла, который будет хранить имя файла'''

    # Объявление адреса для логирования, если не существует, то его создание
    LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(LOG_DIR, exist_ok=True)

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Формат логирования
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s %(filename)s:%(lineno)d')

        # Создание логирования в файл
        file_handler = logging.FileHandler(os.path.join(self.LOG_DIR, name + '.log'), encoding="utf-8")
        file_handler.setFormatter(formatter)

        # Создание логирования в консоль
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)




# Данную функцию вызывать в начале файла, где нужно логирование сразу после импортов, пример logger = get_app_logger()
logger = Logger('user_bot')

