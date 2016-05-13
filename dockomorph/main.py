import os
import sys

from twisted.internet import reactor

from dockomorph import clargs, config, log
from dockomorph.web import server


def main(args=sys.argv[1:], reactor=reactor):
    """
    Automatic deploy from github into Docker containers.
    """
    opts = clargs.parse_args(main.__doc__, args)
    log.init()

    conf = config.parse_config(os.path.expanduser('~/.dockomorph.conf'))

    gh_secret = conf.get('github', {}).get('secret', 'no-secret')

    def gh_event(*a, **kw):
        raise NotImplementedError((gh_event, a, kw))

    ws = server.WebServer(reactor, gh_secret, gh_event)
    ws.listen(opts.port)

    reactor.run()
