import sys

from twisted.internet import reactor

from dockomorph import log
from dockomorph import clargs
from dockomorph.web import server


def main(args=sys.argv[1:], reactor=reactor):
    """
    Automatic deploy from github into Docker containers.
    """
    opts = clargs.parse_args(main.__doc__, args)
    log.init()

    ws = server.WebServer(reactor)
    ws.listen(opts.port)

    reactor.run()
