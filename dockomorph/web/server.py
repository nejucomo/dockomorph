import pkg_resources

from twisted.web import server, static

from dockomorph.log import LogMixin
from dockomorph.web import github, restree


class WebServer (LogMixin):
    StaticDir = pkg_resources.resource_filename('dockomorph', 'web/static')

    def __init__(self, reactor, ghsharedsecret, gh_handle_event):
        LogMixin.__init__(self)
        self._reactor = reactor

        self._site = server.Site(
            restree.build_resource_tree(
                static.File(self.StaticDir),
                {
                    'api': {
                        'github': github.WebhookResource(
                            ghsharedsecret,
                            gh_handle_event,
                        ),
                    },
                },
            ),
        )

        self._site.displayTracebacks = False

    def listen(self, port):
        self._log.info(
            'Listening on port %r; static dir %r',
            port,
            self.StaticDir)
        self._reactor.listenTCP(port, self._site)
