from dockomorph.log import LogMixin


class DockHerd (LogMixin):
    def __init__(self, reactor):
        LogMixin.__init__(self)

        self._reactor = reactor

    def build_and_deploy(self, name, repopath, dockerfile):
        raise NotImplementedError((
            DockHerd.build_and_deploy,
            name,
            repopath,
            dockerfile,
        ))
