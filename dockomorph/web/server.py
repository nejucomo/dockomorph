from twisted.web import server

from dockomorph.web import root
from dockomorph.log import LogMixin


class WebServer (LogMixin):
    def __init__(self, reactor):
        LogMixin.__init__(self)
        self._reactor = reactor
        self._site = server.Site(root.RootResource(reactor))
        self._site.displayTracebacks = False

    def listen(self, port):
        self._log.info(
            'Listening on port %r; static dir %r',
            port,
            root.RootResource.StaticDir)
        self._reactor.listenTCP(port, self._site)
