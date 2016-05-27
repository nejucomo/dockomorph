import sys

from twisted.internet import reactor

from dockomorph import clargs, log, secrets, orchestrator
from dockomorph.web import server


def main(args=sys.argv[1:], reactor=reactor):
    """
    Automatic deploy from github into Docker containers.
    """
    opts = clargs.parse_args(main.__doc__, args)
    log.init()

    ghsecret = secrets.create_or_load_secret('github')

    orch = orchestrator.Orchestrator(reactor)

    ws = server.WebServer(reactor, ghsecret, orch.update_repository)
    ws.listen(opts.port)

    reactor.run()
