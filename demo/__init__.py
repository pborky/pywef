__author__="pborky"
__date__ ="$Feb 21, 2010 6:54:12 PM$"

from action import ACTIONS
from template import TEMPLATES, TEMPLATES_DIR
from logs import LOGS, LOGS_DIR

BASE_DIR = ''.join(__path__)

MONITOR = {
    'force_restart': True,
    'track_files': ( TEMPLATES_DIR, )
}

EXC_WRAPPER = {
    'call': True,
    'init': True
}