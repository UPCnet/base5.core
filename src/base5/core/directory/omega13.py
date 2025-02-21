# NOT USED
# -*- coding: utf-8 -*-
import logging

from AccessControl.Permissions import manage_users
from AccessControl.SecurityInfo import ClassSecurityInfo
from App.class_init import default__class_init__ as InitializeClass
from OFS.Cache import Cacheable
from plone import api
from Products.Five.browser import BrowserView
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService import registerMultiPlugin
from Products.PluggableAuthService.interfaces.plugins import (
    IPropertiesPlugin, IUserEnumerationPlugin)
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from souper.interfaces import ICatalogFactory
from ulearn5.core.utils import get_or_initialize_annotation
from zope.component import getUtility
from zope.interface import Interface, implementer

logger = logging.getLogger('Omega13')


class IOmega13Helper(Interface):
    """Marker interface for Omega13Helper."""


# The Plugin
@implementer(IOmega13Helper, IUserEnumerationPlugin, IPropertiesPlugin)
class Omega13Helper(BasePlugin, Cacheable):
    """ Omega13 PAS Plugin """

    meta_type = 'Omega13 Helper'
    security = ClassSecurityInfo()


    _properties = (
        {
            'id': 'oauth_server',
            'label': 'Oauth Server URL',
            'type': 'string',
            'mode': 'w'
        },
    )

    def __init__(self, id, title=None):
        self._setId(id)
        self.title = title

    security.declarePrivate('enumerateUsers')
    def enumerateUsers(self, id=None, login=None, exact_match=0, sort_by=None, max_results=None, **kw):
        """ Fullfill enumerateUsers requirements """
        # EnumerateUsers Boilerplate
        plugin_id = self.getId()
        view_name = self.getId() + '_enumerateUsers'
        criteria = {'id': id, 'login': login, 'exact_match': exact_match,
                    'sort_by': sort_by, 'max_results': max_results}
        criteria.update(kw)

        cached_info = self.ZCacheable_get(view_name=view_name, keywords=criteria, default=None)

        if cached_info is not None:
            logger.warning('Returning cached results from Omega13 enumerateUsers')
            return cached_info

        user_properties = get_or_initialize_annotation('user_properties')

        result = []
        if exact_match and (id or login):
            if id:
                records = [r for r in user_properties.values() if r.get('username') == id]
            elif login:
                records = [r for r in user_properties.values() if r.get('username') == login]

            if records:
                logger.warning(f'Omega13 found {len(records)} user(s): {records}')
                result.append({'id': records[0]['username'],
                            'login': records[0]['username'],
                            'pluginid': plugin_id})
        else:
            if id:
                records = [r for r in user_properties.values() if r.get('username', '').startswith(id)]
            elif login:
                records = [r for r in user_properties.values() if r.get('username', '').startswith(login)]

            if records:
                logger.warning(f'Omega13 found {len(records)} user(s): {records}')
                for record in records:
                    result.append({'id': record['username'],
                                'login': record['username'],
                                'pluginid': plugin_id})

        result = tuple(result)
        self.ZCacheable_set(result, view_name=view_name, keywords=criteria)

        return result


    security.declarePrivate('getPropertiesForUser')
    def getPropertiesForUser(self, user, request=None):
        """ Fullfill PropertiesPlugin requirements """
        portal = api.portal.get()
        user_properties_utility = getUtility(ICatalogFactory, name='user_properties')
        indexed_attrs = user_properties_utility(portal).keys()
        properties = {}
        user_properties = get_or_initialize_annotation('user_properties')
        user_id = user.getid()
        record = next((r for r in user_properties.values() if r.get('username') == user_id))
        if record:
            for attr in indexed_attrs:
                if record.get(attr, False):
                    properties[attr] = record.get(attr)

        return properties

InitializeClass(Omega13Helper)

# The Zope install part
manage_add_omega13_form = PageTemplateFile('browser/add_plugin', globals(), __name__='manage_add_omega13_form')


def manage_add_omega13_helper(dispatcher, id, title=None, REQUEST=None):
    """Add an omega13 Helper to the PluggableAuthentication Service."""

    sp = Omega13Helper(id, title)
    dispatcher._setObject(sp.getId(), sp)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect('%s/manage_workspace'
                                     '?manage_tabs_message='
                                     'omega13Helper+added.'
                                     % dispatcher.absolute_url())


def register_omega13_plugin():
    try:
        registerMultiPlugin(Omega13Helper.meta_type)
    except RuntimeError:
        # make refresh users happy
        pass


def register_omega13_plugin_class(context):
    context.registerClass(Omega13Helper,
                          permission=manage_users,
                          constructors=(manage_add_omega13_form,
                                        manage_add_omega13_helper),
                          visibility = None,
                          icon='directory/icon.gif')


class ActivateOmega13(BrowserView):

    def ___call__(self):
        portal = self.context
        pas = portal.acl_users
        pluginid = 'omega13'

        installed = pas.objectIds()
        if pluginid in installed:
            return 'Omega 13 already installed.'

        plugin = Omega13Helper(pluginid, title='Omega13 plugin')
        pas._setObject(pluginid, plugin)
        plugin = pas[plugin.getId()]  # get plugin acquisition wrapped!
        for info in pas.plugins.listPluginTypeInfo():
            interface = info['interface']
            if not interface.providedBy(plugin):
                continue
            pas.plugins.activatePlugin(interface, plugin.getId())
            # In case we want to move it to the top
            pas.plugins.movePluginsDown(
                interface,
                [x[0] for x in pas.plugins.listPlugins(interface)[:-1]],
            )
        return 'Yes, captain.'
