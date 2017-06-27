# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface


class IBase5CoreLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""

class IHomePage(Interface):
    """ Marker interface for home page documents """

class IHomePageView(Interface):
    """Marker interface for the Homepage View."""

class IProtectedContent(Interface):
    """Marker interface for preventing dumb users to delete system configuration
       related content
    """

