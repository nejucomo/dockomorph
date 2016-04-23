from twisted.web import static


class RootResource (static.File):
    def __init__(self, reactor):
        raise NotImplementedError(RootResource.__init__)
