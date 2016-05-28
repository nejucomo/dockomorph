from dockomorph.log import LogMixin
from dockomorph import dockherd, repoman


class Orchestrator (LogMixin):
    def __init__(self, reactor, authset):
        LogMixin.__init__(self)

        self._repoman = repoman.RepositoryManager(reactor, authset)
        self._dockherd = dockherd.DockHerd(reactor)

    def update_repository(self, name, repourl, tag):
        d = self._repoman.update_repository(name, repourl, tag)
        d.addCallback(lambda args: self._dockherd.build_and_deploy(*args))
        return d
