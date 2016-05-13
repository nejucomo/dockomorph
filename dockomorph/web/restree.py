from twisted.web import resource


def build_resource_tree(res, children):
    """\
    Concisely specify a tree of web resources.

    @param res: a twisted web resource.
    @param children: a dict of {path, child}. Child is a (recursively
                     structured) dict, or a twisted web resource.

    @return: res
    """

    res.isLeaf = False

    for path, child in children.iteritems():
        if isinstance(child, dict):
            # Create a new generic resource then recursively populate it:
            child = build_resource_tree(resource.Resource(), child)

        res.putChild(path, child)

    return res
