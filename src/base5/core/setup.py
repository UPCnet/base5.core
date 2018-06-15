# -*- coding: utf-8 -*-
import os
import transaction
from five import grok
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.component import getUtility
from zope.component.hooks import getSite
from plone.registry.interfaces import IRegistry

from Products.CMFPlone.interfaces import IPloneSiteRoot, ITinyMCESchema
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IUserAdderPlugin, IPropertiesPlugin
from Products.PlonePAS.interfaces.group import IGroupManagement

from base5.core.utils import add_user_to_catalog
from base5.core.utils import reset_user_catalog
from base5.core.utils import json_response

from plone import api
from souper.soup import get_soup

import pkg_resources
import logging

try:
    pkg_resources.get_distribution('Products.PloneLDAP')
except pkg_resources.DistributionNotFound:
    HAS_LDAP = False
else:
    HAS_LDAP = True
    from Products.PloneLDAP.factory import manage_addPloneLDAPMultiPlugin
    from Products.LDAPUserFolder.LDAPUserFolder import LDAPUserFolder

try:
    pkg_resources.get_distribution('plone.app.contenttypes')
except pkg_resources.DistributionNotFound:
    HAS_DXCT = False
else:
    HAS_DXCT = True
    from plone.dexterity.utils import createContentInContainer

logger = logging.getLogger(__name__)

LDAP_PASSWORD = os.environ.get('ldapbindpasswd', '')


class setupTinyMCEConfigPlone5(grok.View):
    """ Setup view for tinymce config """
    grok.name('setuptinymce')
    grok.context(Interface)
    grok.require('cmf.ManagePortal')

    def render(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass
        settings = getUtility(IRegistry).forInterface(
            ITinyMCESchema,
            prefix="plone",
            check=False
            )
        settings.resizing = True
        settings.autoresize = True
        settings.editor_width = u'100%'
        settings.editor_height = u'250'
        settings.header_styles = [u'Header 2|h2', u'Header 3|h3', u'Header 4|h4']
        settings.formats = u'{"clearfix": {"classes": "clearfix", "block": "div"}, "discreet": {"inline": "span", "classes": "discreet"}, "alerta": {"inline": "span", "classes": "bg-warning", "styles": {"padding": "15px"}}, "banner-minimal": {"inline": "a", "classes": "link-banner-minimal"}, "banner": {"inline": "a", "classes": "link-banner"}, "exit": {"inline": "span", "classes": "bg-success", "styles": {"padding": "15px"}}, "perill": {"inline": "span", "classes": "bg-danger", "styles": {"padding": "15px"}}, "small": {"inline": "small"}, "destacat": {"inline": "p", "classes": "lead"}, "marcat": {"inline": "mark"}, "preformat": {"inline": "pre", "styles": {"outline-style": "none"}}}'
        settings.plugins.append('autosave')
        settings.plugins.append('charmap')
        settings.plugins.append('colorpicker')
        settings.plugins.append('contextmenu')
        settings.plugins.append('directionality')
        settings.plugins.append('emoticons')
        settings.plugins.append('fullpage')
        settings.plugins.append('insertdatetime')
        settings.plugins.append('textcolor')
        settings.plugins.append('textpattern')
        settings.plugins.append('visualblocks')
        settings.toolbar = u'undo redo | styleselect formatselect | fullscreen | code | save | preview | template | cut copy  paste  pastetext | searchreplace  textpattern selectallltr |  removeformat | anchor |  inserttable tableprops deletetable cell row column | rtl |  bold italic underline strikethrough superscript subscript | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | unlink plonelink ploneimage | forecolor backcolor |'
        settings.custom_plugins.append('template|+plone+static/components/tinymce-builded/js/tinymce/plugins/template')
        settings.other_settings = u'{"forced_root_block": false, "cleanup": false, "valid_elements": "*[*]", "valid_children": "+a[img|div|h2|p]"}'
        transaction.commit()

        from Products.CMFPlone.interfaces import IMarkupSchema
        markup_settings = getUtility(IRegistry).forInterface(IMarkupSchema, prefix='plone')
        markup_settings.allowed_types = ('text/html', 'text/x-web-markdown', 'text/x-web-textile')

        return "TinyMCE configuration and markdown applied"


class setupLDAPUPC(grok.View):
    """ Configure LDAPUPC for Plone instance """
    grok.context(IPloneSiteRoot)
    grok.require('zope2.ViewManagementScreens')

    def render(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass
        portal = getSite()

        if HAS_LDAP:
            try:
                manage_addPloneLDAPMultiPlugin(portal.acl_users, 'ldapUPC',
                    title='ldapUPC', use_ssl=1, login_attr='cn', uid_attr='cn', local_groups=0,
                    users_base='ou=Users,dc=upc,dc=edu', users_scope=2,
                    roles='Authenticated', groups_base='ou=Groups,dc=upc,dc=edu',
                    groups_scope=2, read_only=True, binduid='cn=ldap.serveis,ou=users,dc=upc,dc=edu', bindpwd=LDAP_PASSWORD,
                    rdn_attr='cn', LDAP_server='ldap.upc.edu', encryption='SSHA')
                portal.acl_users.ldapUPC.acl_users.manage_edit('ldapUPC', 'cn', 'cn', 'ou=Users,dc=upc,dc=edu', 2, 'Authenticated',
                    'ou=Groups,dc=upc,dc=edu', 2, 'cn=ldap.serveis,ou=users,dc=upc,dc=edu', LDAP_PASSWORD, 1, 'cn',
                    'top,person', 0, 0, 'SSHA', 1, '')

                plugin = portal.acl_users['ldapUPC']

                plugin.manage_activateInterfaces(['IGroupEnumerationPlugin',
                                                  'IGroupsPlugin',
                                                  'IGroupIntrospection',
                                                  'IAuthenticationPlugin',
                                                  'IUserEnumerationPlugin'])

                plugin.ZCacheable_setManagerId('RAMCache')
                # Comentem la linia per a que no afegeixi
                # LDAPUserFolder.manage_addServer(portal.acl_users.ldapUPC.acl_users, 'ldap.upc.edu', '636', use_ssl=1)

                LDAPUserFolder.manage_deleteLDAPSchemaItems(portal.acl_users.ldapUPC.acl_users, ldap_names=['sn'], REQUEST=None)
                LDAPUserFolder.manage_addLDAPSchemaItem(portal.acl_users.ldapUPC.acl_users, ldap_name='sn', friendly_name='Last Name', public_name='name')
                LDAPUserFolder.manage_addLDAPSchemaItem(portal.acl_users.ldapUPC.acl_users, ldap_name='mail', friendly_name='Email Address', public_name='mail')
                LDAPUserFolder.manage_addLDAPSchemaItem(portal.acl_users.ldapUPC.acl_users, ldap_name='cn', friendly_name='Canonical Name', public_name='fullname')

                # Move the ldapUPC to the top of the active plugins.
                # Otherwise member.getProperty('email') won't work properly.
                # from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
                # portal.acl_users.plugins.movePluginsUp(IPropertiesPlugin, ['ldapUPC'])
                # portal.acl_users.plugins.manage_movePluginsUp('IPropertiesPlugin', ['ldapUPC'], context.REQUEST.RESPONSE)
                portal_role_manager = portal.acl_users['portal_role_manager']
                portal_role_manager.assignRolesToPrincipal(['Manager'], 'UPC.Plone.Admins')
                portal_role_manager.assignRolesToPrincipal(['Manager'], 'UPCnet.Plone.Admins')
                portal_role_manager.assignRolesToPrincipal(['Manager'], 'UPCnet.ATIC')
            except:
                logger.debug('Invalid credentials: Try other password')
        else:
            logger.debug('You do not have LDAP libraries in your current buildout configuration. POSOK.')


class setupLDAPExterns(grok.View):
    """ Configure LDAPExterns for Plone instance """
    grok.context(IPloneSiteRoot)
    grok.require('zope2.ViewManagementScreens')

    def render(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass
        portal = getSite()

        if 'branch' in self.request.form and self.request.form['branch'] != '':
            branch = self.request.form['branch']

            users_base='ou=users,ou='+ branch +',dc=upcnet,dc=es'
            groups_base='ou=groups,ou='+ branch +',dc=upcnet,dc=es'
            binduid='cn=ldap,ou='+ branch +',dc=upcnet,dc=es'

            # Delete the LDAPUPC if exists
            if getattr(portal.acl_users, 'ldapUPC', None):
                portal.acl_users.manage_delObjects('ldapUPC')

            # try:
            manage_addPloneLDAPMultiPlugin(portal.acl_users, 'ldapexterns',
                title='ldapexterns', use_ssl=1, login_attr='cn', uid_attr='cn', local_groups=0,
                users_base=users_base, users_scope=2, roles='Authenticated,Member',
                groups_base=groups_base, groups_scope=2, read_only=True, binduid=binduid,
                bindpwd=LDAP_PASSWORD, rdn_attr='cn', LDAP_server='ldap.upcnet.es', encryption='SSHA')
            portal.acl_users.ldapexterns.acl_users.manage_edit('ldapexterns', 'cn',
                'cn', users_base, 2, 'Authenticated,Member', groups_base, 2, binduid,
                LDAP_PASSWORD, 1, 'cn', 'top,person,inetOrgPerson', 0, 0, 'SSHA', 0, '')

            plugin = portal.acl_users['ldapexterns']

            # Activate plugins (all)
            plugin.manage_activateInterfaces(['IAuthenticationPlugin',
                                              'ICredentialsResetPlugin',
                                              'IGroupEnumerationPlugin',
                                              'IGroupIntrospection',
                                              'IGroupManagement',
                                              'IGroupsPlugin',
                                              'IUserAdderPlugin',
                                              'IUserEnumerationPlugin',
                                              'IUserManagement',
                                              'IPropertiesPlugin',
                                              'IRoleEnumerationPlugin',
                                              'IRolesPlugin'])

            # In case to have more than one server for fault tolerance
            # LDAPUserFolder.manage_addServer(portal.acl_users.ldapUPC.acl_users, "ldap.upc.edu", '636', use_ssl=1)

            # Redefine some schema properties
            LDAPUserFolder.manage_deleteLDAPSchemaItems(portal.acl_users.ldapexterns.acl_users, ldap_names=['sn'], REQUEST=None)
            LDAPUserFolder.manage_deleteLDAPSchemaItems(portal.acl_users.ldapexterns.acl_users, ldap_names=['cn'], REQUEST=None)
            LDAPUserFolder.manage_addLDAPSchemaItem(portal.acl_users.ldapexterns.acl_users, ldap_name='sn', friendly_name='Last Name', public_name='fullname')
            LDAPUserFolder.manage_addLDAPSchemaItem(portal.acl_users.ldapexterns.acl_users, ldap_name='cn', friendly_name='Canonical Name')

            # Update the preference of the plugins
            portal.acl_users.plugins.movePluginsUp(IUserAdderPlugin, ['ldapexterns'])
            portal.acl_users.plugins.movePluginsUp(IGroupManagement, ['ldapexterns'])

            # Move the ldapUPC to the top of the active plugins.
            # Otherwise member.getProperty('email') won't work properly.
            # from Products.PluggableAuthService.interfaces.plugins import IPropertiesPlugin
            # portal.acl_users.plugins.movePluginsUp(IPropertiesPlugin, ['ldapUPC'])
            # portal.acl_users.plugins.manage_movePluginsUp('IPropertiesPlugin', ['ldapUPC'], context.REQUEST.RESPONSE)
            # except:
            #     pass

            # Add LDAP plugin cache
            plugin = portal.acl_users['ldapexterns']
            plugin.ZCacheable_setManagerId('RAMCache')

            #Configuracion por defecto de los grupos de LDAP de externs
            groups_query = u'(&(objectClass=groupOfUniqueNames))'
            user_groups_query = u'(&(objectClass=groupOfUniqueNames)(uniqueMember=%s))'
            api.portal.set_registry_record('base5.core.controlpanel.core.IGenwebCoreControlPanelSettings.groups_query', groups_query)
            api.portal.set_registry_record('base5.core.controlpanel.core.IGenwebCoreControlPanelSettings.user_groups_query', user_groups_query)
            return 'Done. groupOfUniqueNames in LDAP Controlpanel Search'


class setupLDAP(grok.View):
    """ Configure basic LDAP for Plone instance """
    grok.context(IPloneSiteRoot)
    grok.require('zope2.ViewManagementScreens')

    def render(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass
        portal = getSite()
        ldap_name = self.request.form.get('ldap_name', 'ldap')
        ldap_server = self.request.form.get('ldap_server')
        branch_name = self.request.form.get('branch_name')
        base_dn = self.request.form.get('base_dn')
        branch_admin_cn = self.request.form.get('branch_admin_cn')
        branch_admin_password = self.request.form.get('branch_admin_password')
        allow_manage_users = self.request.form.get('allow_manage_users', False)

        users_base = 'ou=users,ou={},{}'.format(branch_name, base_dn)
        groups_base = 'ou=groups,ou={},{}'.format(branch_name, base_dn)
        bind_uid = 'cn={},ou={},{}'.format(branch_admin_cn, branch_name, base_dn)

        # Delete if exists
        if getattr(portal.acl_users, ldap_name, None):
            portal.acl_users.manage_delObjects('ldapUPC')

        manage_addPloneLDAPMultiPlugin(
            portal.acl_users, ldap_name,
            use_ssl=1, login_attr='cn', uid_attr='cn', local_groups=0,
            rdn_attr='cn', encryption='SSHA', read_only=True,
            roles='Authenticated,Member', groups_scope=2, users_scope=2,
            title=ldap_name,
            LDAP_server=ldap_server,
            users_base=users_base,
            groups_base=groups_base,
            binduid=bind_uid,
            bindpwd=branch_admin_password)

        ldap_acl_users = getattr(portal.acl_users, ldap_name).acl_users
        ldap_acl_users.manage_edit(
            ldap_name, 'cn', 'cn', users_base, 2, 'Authenticated,Member',
            groups_base, 2, bind_uid, branch_admin_password, 1, 'cn',
            'top,person,inetOrgPerson', 0, 0, 'SSHA', 0, '')

        plugin = portal.acl_users[ldap_name]

        active_plugins = [
            'IAuthenticationPlugin', 'ICredentialsResetPlugin', 'IGroupEnumerationPlugin',
            'IGroupIntrospection', 'IGroupManagement', 'IGroupsPlugin',
            'IPropertiesPlugin', 'IRoleEnumerationPlugin', 'IRolesPlugin',
            'IUserAdderPlugin', 'IUserEnumerationPlugin']

        if allow_manage_users:
            active_plugins.append('IUserManagement')

        plugin.manage_activateInterfaces(active_plugins)

        # Redefine some schema properties

        LDAPUserFolder.manage_deleteLDAPSchemaItems(ldap_acl_users, ldap_names=['sn'], REQUEST=None)
        LDAPUserFolder.manage_deleteLDAPSchemaItems(ldap_acl_users, ldap_names=['cn'], REQUEST=None)
        LDAPUserFolder.manage_addLDAPSchemaItem(ldap_acl_users, ldap_name='sn', friendly_name='Last Name', public_name='fullname')
        LDAPUserFolder.manage_addLDAPSchemaItem(ldap_acl_users, ldap_name='cn', friendly_name='Canonical Name')

        # Update the preference of the plugins
        portal.acl_users.plugins.movePluginsUp(IUserAdderPlugin, [ldap_name])
        portal.acl_users.plugins.movePluginsUp(IGroupManagement, [ldap_name])

        # Add LDAP plugin cache
        plugin = portal.acl_users[ldap_name]
        plugin.ZCacheable_setManagerId('RAMCache')
        return 'Done.'


class view_user_catalog(grok.View):
    """ Rebuild the OMEGA13 repoze.catalog for user properties data """
    grok.context(IPloneSiteRoot)
    grok.name('view_user_catalog')
    grok.require('cmf.ManagePortal')

    @json_response
    def render(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass
        portal = api.portal.get()
        soup = get_soup('user_properties', portal)
        records = [r for r in soup.data.items()]

        result = {}
        for record in records:
            item = {}
            for key in record[1].attrs:
                item[key] = record[1].attrs[key]

            result[record[1].attrs['id']] = item

        return result


class reset_user_catalog(grok.View):
    """ Reset the OMEGA13 repoze.catalog for user properties data """

    grok.context(IPloneSiteRoot)
    grok.name('reset_user_catalog')
    grok.require('cmf.ManagePortal')

    def render(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass

        from base5.core.utils import reset_user_catalog
        reset_user_catalog()
        return 'Done.'


class rebuild_user_catalog(grok.View):
    """ Rebuild the OMEGA13 repoze.catalog for user properties data

        For default, we use the mutable_properties (users who have entered into communities)

        Path directo del plugin:
        acl_users/plugins/manage_plugins?plugin_type=IPropertiesPlugin

        En ACL_USERS / LDAP / Properties / Active Plugins ha de estar ordenado así:
          mutable_properties / auto_group / ldapaspb

        But really, we use the most preferent plugin
        If the most preferent plugin is:
           mutable_properties --> users who have entered into communities
           ldap --> users in LDAP
    """
    grok.context(IPloneSiteRoot)
    grok.name('rebuild_user_catalog')
    grok.require('cmf.ManagePortal')

    def render(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass
        portal = api.portal.get()
        plugins = portal.acl_users.plugins.listPlugins(IPropertiesPlugin)
        # We use the most preferent plugin
        # If the most preferent plugin is:
        #    mutable_properties --> users who have entered into communities
        #    ldap --> users in LDAP
        pplugin = plugins[0][1]
        all_user_properties = pplugin.enumerateUsers()

        for user in all_user_properties:
            user.update(dict(username=user['id']))
            if 'title' in user:
                user.update(dict(fullname=user['title']))
            elif 'fullname' in user:
                user.update(dict(fullname=user['fullname']))
            elif 'sn' in user:
                user.update(dict(fullname=user['sn']))
            else:
                user.update(dict(fullname=user['cn']))

            user_obj = api.user.get(user['id'])

            if user_obj:
                add_user_to_catalog(user_obj, user)
            else:
                print('No user found in user repository (LDAP) {}'.format(user['id']))

            print('Updated properties catalog for {}'.format(user['id']))


class DeleteUserPropertiesCatalog(grok.View):
    """ Delete users in catalog not in LDAP.

        Path directo del plugin:
        acl_users/plugins/manage_plugins?plugin_type=IPropertiesPlugin

        En ACL_USERS / LDAP / Properties / Active Plugins ha de estar ordenado así:
          mutable_properties / auto_group / ldapaspb

    """
    grok.context(IPloneSiteRoot)
    grok.name('delete_user_catalog')
    grok.require('cmf.ManagePortal')

    def render(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass

        portal = api.portal.get()
        plugins = portal.acl_users.plugins.listPlugins(IPropertiesPlugin)
        # We use the ldap plugin
        pplugin = plugins[2][1]
        results = []
        try:
            acl = pplugin._getLDAPUserFolder()

            soup = get_soup('user_properties', portal)
            records = [r for r in soup.data.items()]

            for record in records:
                # For each user in catalog search user in ldap
                user_obj = acl.getUserById(record[1].attrs['id'])
                if not user_obj:
                    print('No user found in user repository (LDAP) {}'.format(record[1].attrs['id']))
                    soup.__delitem__(record[1])
                    print('User delete soup {}'.format(record[1].attrs['id']))
                    results.append('User delete soup: {}'.format(record[1].attrs['id']))

            print('Finish rebuild_user_catalog')
            results.append('Finish rebuild_user_catalog')
            return '\n'.join([str(item) for item in results])
        except:
            print('The order to the plugins in En ACL_USERS / LDAP / Properties / Active Plugins : mutable_properties / auto_group / ldapaspb')
            results.append('The order to the plugins in En ACL_USERS / LDAP / Properties / Active Plugins : mutable_properties / auto_group / ldapaspb')
            return '\n'.join([str(item) for item in results])
