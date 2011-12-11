__author__="peterb"
__date__ ="$8.3.2010 14:23:45$"

import logging
import logging.handlers
import os
import os.path

def set_logger(logger_name, filename, max_bytes = 500000, backup_count = 5, full_path = False):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    datefmt = '%Y-%m-%d %H:%M:%S'
    if full_path:
        fmt = '[%(asctime)s]:[%(levelname)s]:[%(name)s]:[in `%(pathname)s` line %(lineno)d]:: %(message)s'
    else:
        fmt = '[%(asctime)s]:[%(levelname)s]:[%(name)s]:[%(filename)s:%(lineno)d]:: %(message)s'
    formatter = logging.Formatter(fmt, datefmt)
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    handler = logging.handlers.RotatingFileHandler(filename, maxBytes=max_bytes, backupCount=backup_count)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def get_logger(logger_name):
    return logging.getLogger(logger_name)





