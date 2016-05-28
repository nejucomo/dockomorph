from dockomorph.log import LogMixin


class ReactiveMixin (LogMixin):
    def __init__(self, reactor):
        LogMixin.__init__(self)
        self._reactor = reactor
