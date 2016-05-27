from dockomorph.log import LogMixin


class RepositoryManager (LogMixin):
    def __init__(self, reactor):
        LogMixin.__init__(self)

        self._reactor = reactor

    def update_repository(self, name, repourl, tag):
        raise NotImplementedError((
            RepositoryManager.update_repository,
            name,
            repourl,
            tag,
        ))
