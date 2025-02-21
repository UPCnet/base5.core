# -*- coding: utf-8 -*-
from base5.core import _
from plone.app.contenttypes.interfaces import ILink
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.indexer import indexer
from plone.supermodel import model
from zope import schema
from zope.component import adapter
from zope.interface import alsoProvides, implementer


class IOpenLinkInNewWindow(model.Schema):
    """Añade el campo 'open in new window' al contenido de link.
    """
    directives.order_after(open_link_in_new_window='remoteUrl')
    open_link_in_new_window = schema.Bool(
        title=_("open_link_in_new_window"),
        description=_("help_open_link_in_new_window"),
        required=False,
        default=False
    )

alsoProvides(IOpenLinkInNewWindow, IFormFieldProvider)


@implementer(IOpenLinkInNewWindow)
@adapter(ILink)
class OpenLinkInNewWindow(object):

    def __init__(self, context):
        self.context = context

    def _set_open_link_in_new_window(self, value):
        self.context.open_link_in_new_window = value

    def _get_open_link_in_new_window(self):
        return getattr(self.context, 'open_link_in_new_window', None)

    open_link_in_new_window = property(_get_open_link_in_new_window, _set_open_link_in_new_window)


@indexer(ILink)
def open_link_in_new_window(obj):
    return obj.open_link_in_new_window
