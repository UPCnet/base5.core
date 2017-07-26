from plone.resource.traversal import ResourceTraverser


class ComponentsTraverser(ResourceTraverser):
    """The web components resource traverser.

    Allows traversal to /++components++<name> using ``plone.resource`` to fetch
    things stored either on the filesystem or in the ZODB.
    """

    name = 'components'
