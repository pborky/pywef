__author__="pborky"
__date__ ="$24.3.2010 0:11:50$"

import os.path

LOGS_DIR = ''.join(__path__)
LOGS = {
    'pywef': {
        'file': {
            'name': os.path.join(LOGS_DIR, 'pywef.log'),
            'size': 5000000,
            'count': 5 } } }
