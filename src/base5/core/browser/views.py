# -*- coding: utf-8 -*-
from five import grok
from plone import api
from Acquisition import aq_inner
from DateTime.DateTime import DateTime
#from scss import Scss

from zope.interface import Interface
from zope.contentprovider import interfaces
from zope.component import getMultiAdapter, queryMultiAdapter, getUtility, queryUtility
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile as ZopeViewPageTemplateFile

from plone.batching import Batch
from plone.registry.interfaces import IRegistry
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer
from plone.app.layout.globals.layout import LayoutPolicy
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.app.layout.navigation.interfaces import INavigationRoot

from Products.CMFPlone import utils
from Products.CMFPlone.utils import safe_unicode
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.PythonScripts.standard import url_quote_plus
# from Products.ATContentTypes.interfaces.event import IATEvent
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone.browser.navigation import CatalogNavigationTabs
from Products.CMFPlone.browser.navigation import get_id, get_view_url
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from base5.core.utils import genweb_config, pref_lang
from base5.core.interfaces import INewsFolder

from base5.core.interfaces import IBase5CoreLayer
from base5.core.browser.interfaces import IHomePage, IHomePageView

from base5.core.browser.manager import ISpanStorage

from Products.CMFCore.interfaces import IFolderish
from plone.memoize.view import memoize
from plone.memoize import ram

import pkg_resources
import json
#import scss

grok.templatedir("views_templates")


class GWConfig(grok.View):
    grok.context(Interface)
    grok.layer(IBase5CoreLayer)

    def render(self):
        return genweb_config()


class HomePageBase(grok.View):

    """
    Base methods for ease the extension of the genweb homePage view. Just
    define a new class inheriting from this one and redefine the basic
    grokkers like:

    class homePage(HomePageBase):
        grok.implements(IHomePageView)
        grok.context(IPloneSiteRoot)
        grok.require('genweb.authenticated')
        grok.layer(IUlearnTheme)

    Overriding the one in this module (homePage) with a more specific
    interface.
    """

    grok.baseclass()

    def update(self):
        self.portlet_container = self.getPortletContainer()

    def getPortletContainer(self):
        context = aq_inner(self.context)
        container = context

        # Portlet container will be in the context,
        # Except in the portal root, when we look for an alternative
        if INavigationRoot.providedBy(self.context):
            pc = getToolByName(context, 'portal_catalog')
            # Add the use case of mixin types of IHomepages. The main ones of a
            # non PAM-enabled site and the possible inner ones.
            result = pc.searchResults(object_provides=IHomePage.__identifier__,
                                      portal_type='Document',
                                      Language=pref_lang())
            if result:
                # Return the object without forcing a getObject()
                container = getattr(context, result[0].id, context)

        return container

    def renderProviderByName(self, provider_name):
        provider = queryMultiAdapter(
            (self.portlet_container, self.request, self),
            interfaces.IContentProvider, provider_name)

        provider.update()

        return provider.render()

    def getSpanValueForManager(self, manager):
        portletManager = getUtility(IPortletManager, manager)
        spanstorage = getMultiAdapter((self.portlet_container, portletManager), ISpanStorage)
        span = spanstorage.span
        if span:
            return span
        else:
            return '4'

    def have_portlets(self, manager_name, view=None):
        """Determine whether a column should be shown. The left column is called
        plone.leftcolumn; the right column is called plone.rightcolumn.
        """
        force_disable = self.request.get('disable_' + manager_name, None)
        if force_disable is not None:
            return not bool(force_disable)

        context = self.portlet_container
        if view is None:
            view = self

        manager = queryUtility(IPortletManager, name=manager_name)
        if manager is None:
            return False

        renderer = queryMultiAdapter((context, self.request, view, manager), IPortletManagerRenderer)
        if renderer is None:
            renderer = getMultiAdapter((context, self.request, self, manager), IPortletManagerRenderer)

        return renderer.visible

    def is_visible(self):
        """ This method lookup for the physical welcome page and checks if the
            user has the permission to view it. If it doesn't raises an
            unauthorized (login)
        """
        portal = api.portal.get()
        pc = api.portal.get_tool('portal_catalog')
        result = pc.unrestrictedSearchResults(object_provides=IHomePage.__identifier__,
                                              Language=pref_lang())
        if result:
            portal.restrictedTraverse(result[0].getPath())
            return True
        else:
            return False


class homePage(HomePageBase):
    """ This is the special view for the homepage containing support for the
        portlet managers provided by the package genweb.portlets.
        It's restrained to IGenwebTheme layer to prevent it will interfere with
        the one defined in the Genweb legacy theme (v3.5).
    """
    grok.name('homepage')
    grok.implements(IHomePageView)
    grok.context(INavigationRoot)
    grok.layer(IBase5CoreLayer)


# class subHomePage(HomePageBase):
#     """ This is the special view for the subhomepage containing support for the
#         portlet managers provided by the package genweb.portlets.
#         This is the PAM aware default LRF homepage view.
#         It is also used in IFolderish (DX and AT) content for use in inner landing
#         pages.
#     """
#     grok.name('homepage')
#     grok.implements(IHomePageView)
#     grok.context(IFolderish)
#     grok.layer(IBase5CoreLayer)
