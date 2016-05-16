import sys

from twisted.internet import reactor

from dockomorph import clargs, log, secrets
from dockomorph.web import server


def main(args=sys.argv[1:], reactor=reactor):
    """
    Automatic deploy from github into Docker containers.
    """
    opts = clargs.parse_args(main.__doc__, args)
    log.init()

    ghsecret = secrets.create_or_load_secret('github')

    def gh_event(*a, **kw):
        raise NotImplementedError((gh_event, a, kw))

    ws = server.WebServer(reactor, ghsecret, gh_event)
    ws.listen(opts.port)

    reactor.run()
