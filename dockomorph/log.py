import sys
import logging

from twisted.python import log as twistedlog


LogFormat = '%(asctime)s %(levelname) 5s %(name)s | %(message)s'
DateFormat = '%Y-%m-%dT%H:%M:%S%z'


def init():
    logging.basicConfig(
        stream=sys.stdout,
        format=LogFormat,
        datefmt=DateFormat,
        level=logging.DEBUG)

    twistedlog.PythonLoggingObserver().start()


class LogMixin (object):
    def __init__(self, instanceinfo=None):
        name = type(self).__name__
        if instanceinfo:
            name = '{}[{}]'.format(name, instanceinfo)

        self._log = logging.getLogger(name)
        self._log.debug('__init__')
