from dockomorph.reactive import ReactiveMixin


class DockHerd (ReactiveMixin):
    def build_and_deploy(self, repopath):
        raise NotImplementedError((
            DockHerd.build_and_deploy,
            repopath,
        ))
