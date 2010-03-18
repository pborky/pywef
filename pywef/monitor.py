import os.path
__author__="pborky"
__date__ ="$22.2.2010 3:22:45$"

import os
import sys
import signal
import threading
import atexit
import Queue

class DummyLogger(object):
    def write(self, msg):
        print >> sys.stderr,  '\n%s' % msg

    def debug(self, msg):
        self.write('DEBUG: %s' % msg)

    def info(self, msg):
        self.write('INFO: %s' % msg)

    def warn(self, msg):
        self.write('WARN: %s' % msg)

    def error(self, msg):
        self.write('ERROR: %s' % msg)

class Monitor(object):
    """
    Class monitoring loaded modules and additional files for modification.
    Interpreter process is restarted in case of change detection.
    """
    
    def __init__(self, restart = None, reload = None, logger = None, force_restart = True, sig = None):
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

        if logger is None:
            self._logger = DummyLogger()
        else:
            self._logger = logger
        
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
        self._logger.info('Triggering process restart.')
        os.kill(os.getpid(), self._signal)

    def _reload(self, module = None, module_name = None, **kw):
        if module is not None:
            if module_name is not None:
                raise TypeError('You must pass either \'module\' or \'module_name\' argument.')
            self._logger.info('Triggering module reload.')
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
                    self._logger.info('Change detected to \'%s\'.' % path)
                    self._do_reload(module=module)


            # Check modification times on files which have
            # specifically been registered for monitoring.

            for path in self._files:
                if self._modified(path):
                    self._logger.info('Change detected to \'%s\'.' % path)
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
            os.path.walk(path, self._add_file, None)
        else:
            if not path in self._files:
                self._files.append(path)

    def _add_file(self, arg, dirname, names):
        for name in names:
            path = '%s%s' % (dirname, name)
            if not path in self._files:
                self._logger.info('Tracking file: "%s".' % path)
                self._files.append(path)

    def start(self, interval=1.0):
        """ Start monitoring """

        self._interval = interval
        
        self._lock.acquire()
        
        if not self._running:
            self._logger.info('Starting change monitor.')
            self._running = True
            self._thread.start()
        
        self._lock.release()
