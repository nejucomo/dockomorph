import sys

from twisted.internet import reactor

from dockomorph import log
from dockomorph import clargs


def main(args=sys.argv[1:], reactor=reactor):
    """
    Automatic deploy from github into Docker containers.
    """
    clargs.parse_args(main.__doc__, args)
    log.init()
    reactor.run()
