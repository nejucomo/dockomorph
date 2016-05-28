from dockomorph import paths
from dockomorph.run import ShellExecutorMixin
from dockomorph.gpg import GitGpgAuthorizer


class RepositoryManager (ShellExecutorMixin):
    def __init__(self, reactor, authset):
        ShellExecutorMixin.__init__(self, reactor)
        self._gga = GitGpgAuthorizer(reactor, authset)

    def update_repository(self, name, repourl, tag):
        repodir = paths.GitsDir.child(name)
        if repodir.isdir():
            d = self.run(
                paths.GitExec,
                ['fetch', repourl, tag],
                path=repodir)
        else:
            d = self.run(
                paths.GitExec,
                ['clone', '--branch', tag, '--', repourl, name],
                path=paths.GitsDir)

        d.addCallback(
            lambda _: self._gga.check_tag_signature(repodir, tag),
        )

        d.addCallback(lambda _: repodir)
        return d
