__author__="peterb"
__date__ ="$8.3.2010 14:23:45$"

import logging
import logging.handlers

def set_logger(logger_name, filename, max_bytes = 500000, backup_count = 5):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] %(name)s [%(levelname)s]\t[%(module)s.%(funcName)s] (%(filename)s:%(lineno)d): %(message)s', '%Y-%m-%d %H:%M:%S')
    handler = logging.handlers.RotatingFileHandler(filename, maxBytes=max_bytes, backupCount=backup_count)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def get_logger(logger_name):
    return logging.getLogger(logger_name)





