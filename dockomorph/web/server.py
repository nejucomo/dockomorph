import pkg_resources

from twisted.web import server, static

from dockomorph.log import LogMixin


class WebServer (LogMixin):
    StaticDir = pkg_resources.resource_filename('dockomorph', 'web/static')

    def __init__(self, reactor):
        LogMixin.__init__(self)
        self._reactor = reactor

        root = static.File(self.StaticDir)
        root.isLeaf = False

        self._site = server.Site(root)
        self._site.displayTracebacks = False

    def listen(self, port):
        self._log.info(
            'Listening on port %r; static dir %r',
            port,
            self.StaticDir)
        self._reactor.listenTCP(port, self._site)
