__author__="pborky"
__date__ ="$22.2.2010 3:22:45$"

import os
import sys
import signal
import threading
import atexit
import Queue
from pywef.logger import get_logger

logger = get_logger('pywef')

class Monitor:
    """
    Class monitoring loaded modules and additional files for modification.
    Interpreter process is restarted in case of change detection.
    """
    
    def __init__(self):
        self._interval = 1.0
        self._times = {}
        self._files = []

        self._running = False
        self._queue = Queue.Queue()
        self._lock = threading.Lock()

        atexit.register(self._exiting)

        self._thread = threading.Thread(target=self._monitor)
        self._thread.setDaemon(True)

    def _restart(self, path):
        self._queue.put(True)
        prefix = '[%s (pid=%d)]:' % (self.__class__.__name__ ,os.getpid())

        logger.info('Change detected to \'%s\'.' % path)
        logger.info('Triggering process restart.')
        
        os.kill(os.getpid(), signal.SIGINT)

    def _modified(self,path):
        try:
            # If path doesn't denote a file and were previously
            # tracking it, then it has been removed or the file type
            # has changed so force a restart. If not previously
            # tracking the file then we can ignore it as probably
            # pseudo reference such as when file extracted from a
            # collection of modules contained in a zip file.

            if not os.path.isfile(path):
                return path in self._times

            # Check for when file last modified.

            mtime = os.stat(path).st_mtime
            if path not in self._times:
                self._times[path] = mtime

            # Force restart when modification time has changed, even
            # if time now older, as that could indicate older file
            # has been restored.

            if mtime != self._times[path]:
                return True
        except:
            # If any exception occured, likely that file has been
            # been removed just before stat(), so force a restart.

            return True

        return False

    def _monitor(self):
        while 1:
            # Check modification times on all files in sys.modules.

            for module in sys.modules.values():
                if not hasattr(module, '__file__'):
                    continue
                path = getattr(module, '__file__')
                if not path:
                    continue
                if os.path.splitext(path)[1] in ['.pyc', '.pyo', '.pyd']:
                    path = path[:-1]
                if self._modified(path):
                    return self._restart(path)

            # Check modification times on files which have
            # specifically been registered for monitoring.

            for path in self._files:
                if self._modified(path):
                    return self._restart(path)

            # Go to sleep for specified interval.

            try:
                return self._queue.get(timeout=self._interval)
            except:
                pass

    def _exiting(self):
        try:
            self._queue.put(True)
        except:
            pass
        self._thread.join()

    def track(self, path):
        """ Add additional file to track """

        if not path in _files:
            self._files.append(path)

    def start(self, interval=1.0):
        """ Start monitoring """

        self._interval = interval
        
        self._lock.acquire()
        
        if not self._running:
            logger.info('Starting change monitor.')
            self._running = True
            self._thread.start()
        
        self._lock.release()
