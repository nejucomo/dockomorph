import pkg_resources

from twisted.web import static


class RootResource (static.File):
    StaticDir = pkg_resources.resource_filename('dockomorph', 'static')

    def __init__(self, reactor):
        self._reactor = reactor
        static.File.__init__(self, self.StaticDir)
