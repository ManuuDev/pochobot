import logging as logging
import time
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

mainlog: logging.Logger


def log(message, level: int = logging.INFO):
    global mainlog

    mainlog.log(msg=message, level=level)


def create_main_log():
    global mainlog

    mainlog = create_log('mainlog')


def create_log(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    rotation_loggin = TimedRotatingFileHandler('bot.log', when='midnight', backupCount=3)
    rotation_loggin.suffix = '%Y-%m-%d.log'

    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    rotation_loggin.setFormatter(formatter)

    rotation_loggin.setLevel(logging.INFO)

    current_time = int(time.time())
    rotation_time = rotation_loggin.computeRollover(current_time)
    print('Next log rotation: {}'.format(datetime.fromtimestamp(rotation_time)))

    logger.addHandler(rotation_loggin)

    return logger
