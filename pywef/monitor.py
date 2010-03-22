import os.path
__author__="pborky"
__date__ ="$22.2.2010 3:22:45$"

import os
import sys
import signal
import threading
import atexit
import Queue
from logger import get_logger

log = get_logger('pywef.monitor')

class Monitor(object):
    """
    Class monitoring loaded modules and additional files for modification.
    Interpreter process is restarted in case of change detection.
    """
    
    def __init__(self, restart = None, reload = None, force_restart = True, sig = None):
        self._interval = 1.0
        self._times = {}
        self._files = []

        self._running = False
        self._queue = Queue.Queue()
        self._lock = threading.Lock()

        atexit.register(self._exiting)

        self._thread = threading.Thread(target=self._monitor)
        self._thread.setDaemon(True)

        if sig is None:
            self._signal = signal.SIGTERM
        else:
            self._signal = sig
        
        if restart is None:
            self._do_restart = self._restart
        else:
            self._do_restart = restart
        
        if reload is None:
            if force_restart:
                self._do_reload = self._restart
            else:
                self._do_reload = self._reload
        else:
            if force_restart:
                raise TypeError('If \'force_restart\' is given \'reload\' argument must be None.')
            self._do_reload = reload

    def _restart(self, **kw):
        self._queue.put(True)
        log.info('Triggering process restart.')
        os.kill(os.getpid(), self._signal)

    def _reload(self, module = None, module_name = None, **kw):
        if module is not None:
            if module_name is not None:
                raise TypeError('You must pass either \'module\' or \'module_name\' argument.')
            log.info('Triggering module reload.')
            reload(module)
        else:
            if module_name is None:
                raise TypeError('You must pass either \'module\' or \'module_name\' argument.')
            return

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
                self._times[path] = mtime
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
                    log.info('Change detected to \'%s\'.' % path)
                    self._do_reload(module=module)


            # Check modification times on files which have
            # specifically been registered for monitoring.

            for path in self._files:
                if self._modified(path):
                    log.info('Change detected to \'%s\'.' % path)
                    self._do_restart()

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
        if os.path.isdir(path):
            self._walk_dir(path)
        else:
            self._add_file(path)

    def _walk_dir(self, path):
        for file in os.listdir(path):
            if not file.startswith('.'):
                filename = os.path.join(path, file)
                if os.path.isdir(filename):
                    self._walk_dir(filename)
                else:
                    self._add_file(filename)

    def _add_file(self, filename):
        if not filename in self._files:
            log.info('Tracking file: "%s".' % filename)
            self._files.append(filename)
                    

    def start(self, interval=1.0):
        """ Start monitoring """

        self._interval = interval
        
        self._lock.acquire()
        
        if not self._running:
            log.info('Starting change monitor.')
            self._running = True
            self._thread.start()
        
        self._lock.release()
