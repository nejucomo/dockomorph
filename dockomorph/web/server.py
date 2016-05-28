import pkg_resources

from twisted.web import server, static

from dockomorph.reactive import ReactiveMixin
from dockomorph.web import github, restree


class WebServer (ReactiveMixin):
    StaticDir = pkg_resources.resource_filename('dockomorph', 'web/static')

    def __init__(self, reactor, ghsharedsecret, gh_handle_event):
        ReactiveMixin.__init__(self, reactor)

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
