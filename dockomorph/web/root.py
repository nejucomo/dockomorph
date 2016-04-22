import pkg_resources

from twisted.web import resource, static


class RootResource (resource.Resource):
    StaticDir = pkg_resources.resource_filename('dockomorph', 'web/static')

    # Twisted API flags:
    isLeaf = False

    def __init__(self, reactor):
        self._reactor = reactor
        resource.Resource.__init__(self)

        self._statres = static.File(self.StaticDir)

    def getChild(self, path, request):
        # Note: This is only called when explicit putChild children
        # aren't found, so those override self._statres:
        return self._statres.getChild(path, request)
