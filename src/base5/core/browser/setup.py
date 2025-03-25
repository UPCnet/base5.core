# -*- coding: utf-8 -*-
import logging
import os
import urllib
import uuid

import pkg_resources
import transaction
from base5.core.utils import (add_user_to_catalog, convertSquareImage,
                              get_safe_member_by_id, json_response,
                              remove_user_from_catalog)
from mrs5.max.utilities import IMAXClient
from OFS.Image import Image
from plone import api
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFPlone.interfaces import (IFilterSchema, IPloneSiteRoot,
                                          ITinyMCESchema)
from Products.Five.browser import BrowserView
from Products.PlonePAS.interfaces.group import IGroupManagement
from Products.PluggableAuthService.interfaces.plugins import (
    IPropertiesPlugin, IUserAdderPlugin)
from ulearn5.core.gwuuid import IGWUUID
from ulearn5.core.patches import deleteMembers
from ulearn5.core.utils import get_or_initialize_annotation
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import alsoProvides
from repoze.catalog.query import Eq
from souper.soup import get_soup
from souper.soup import Record

try:
    pkg_resources.get_distribution('Products.PloneLDAP')
except pkg_resources.DistributionNotFound:
    HAS_LDAP = False
else:
    HAS_LDAP = True
    from Products.LDAPUserFolder.LDAPUserFolder import LDAPUserFolder
    from Products.PloneLDAP.factory import manage_addPloneLDAPMultiPlugin

try:
    pkg_resources.get_distribution('plone.app.contenttypes')
except pkg_resources.DistributionNotFound:
    HAS_DXCT = False
else:
    HAS_DXCT = True
    from plone.dexterity.utils import createContentInContainer

logger = logging.getLogger(__name__)

LDAP_PASSWORD = os.environ.get('ldapbindpasswd', '')


class addUserPropertiesCatalog(BrowserView):
    """ Rebuild the OMEGA13 repoze.catalog for specific user properties data

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

    def __call__(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass

        if 'users' in self.request.form:
            portal = api.portal.get()
            plugins = portal.acl_users.plugins.listPlugins(IPropertiesPlugin)

            # We use the most preferent plugin
            # If the most preferent plugin is:
            #    mutable_properties --> users who have entered into communities
            #    ldap --> users in LDAP
            pplugin = plugins[-1][1]

            usersid = self.request.form['users'].split(',')
            msg = ''
            for userid in usersid:
                user_properties = pplugin.enumerateUsers(id=userid)
                for user in user_properties:
                    if user['id'] == userid:
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
                            print('Updated properties catalog for ' + user['id'])
                            msg += user['id'] + ': Ok\n'

                        else:
                            print('No user found in user repository (LDAP) ' + user['id'])
                            msg += user['id'] + ': Error\n'

            print('Finish add_user_catalog')
            if msg != '':
                self.context.plone_utils.addPortalMessage(msg, 'info')


class removeUserPropertiesCatalog(BrowserView):
    """ Remove specific user in catalog.
    """

    def __call__(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass

        if 'users' in self.request.form:
            users = self.request.form['users'].split(',')

            msg = ''
            for username in users:
                remove_user_from_catalog(username)
                print('Delete properties catalog for ' + username)
                msg += username + ': Ok\n'

            print('Finish remove_user_catalog')
            if msg != '':
                self.context.plone_utils.addPortalMessage(msg, 'info')


class setupTinyMCEConfigPlone5(BrowserView):
    """ Setup view for tinymce config """

    def __call__(self):
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
        settings.autoresize = False
        settings.editor_width = u'100%'
        settings.editor_height = u'500'
        settings.header_styles = [u'Header 2|h2', u'Header 3|h3', u'Header 4|h4']
        settings.formats = u'{"clearfix": {"classes": "clearfix", "block": "div"}, "discreet": {"inline": "span", "classes": "discreet"}, "alerta": {"inline": "span", "classes": "bg-warning", "styles": {"padding": "15px"}}, "banner-minimal": {"inline": "a", "classes": "link-banner-minimal"}, "banner": {"inline": "a", "classes": "link-banner"}, "exit": {"inline": "span", "classes": "bg-success", "styles": {"padding": "15px"}}, "perill": {"inline": "span", "classes": "bg-danger", "styles": {"padding": "15px"}}, "small": {"inline": "small"}, "destacat": {"inline": "p", "classes": "lead"}, "marcat": {"inline": "mark"}, "preformat": {"inline": "pre", "styles": {"outline-style": "none"}}}'
        settings.plugins.append('autosave')
        settings.plugins.append('charmap')
        settings.plugins.append('colorpicker')
        settings.plugins.append('contextmenu')
        settings.plugins.append('directionality')
        settings.plugins.append('emoticons')
        settings.plugins.append('insertdatetime')
        settings.plugins.append('textcolor')
        settings.plugins.append('textpattern')
        settings.plugins.append('visualblocks')
        settings.toolbar = u'undo redo | styleselect formatselect | fullscreen | code | save | preview | template | cut copy  paste  pastetext | searchreplace  textpattern selectallltr |  removeformat | anchor |  inserttable tableprops deletetable cell row column | rtl |  bold italic underline strikethrough superscript subscript | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | unlink plonelink ploneimage | forecolor backcolor |'
        settings.custom_plugins.append('template|+plone+static/components/tinymce-builded/js/tinymce/plugins/template')
        settings.other_settings = u'{"forced_root_block": "p", "cleanup": false, "valid_elements": "*[*]", "valid_children": "+a[img|div|h2|p]"}'

        filter_settings = getUtility(IRegistry).forInterface(
            IFilterSchema,
            prefix="plone",
            check=False
        )

        filter_settings.nasty_tags = [u'object', u'embed', u'applet', u'script', u'meta']
        filter_settings.valid_tags = [u'a', u'abbr', u'acronym', u'address', u'article', u'aside', u'audio', u'b', u'bdo', u'big', u'blockquote', u'body', u'br', u'canvas', u'caption', u'cite', u'code', u'col', u'colgroup', u'command', u'datalist', u'dd', u'del', u'details', u'dfn', u'dialog', u'div', u'dl', u'dt', u'em', u'figure', u'footer', u'h1', u'h2', u'h3', u'h4', u'h5', u'h6', u'head', u'header', u'hgroup', u'html', u'i', u'iframe', u'img', u'ins', u'kbd', u'keygen', u'li', u'map', u'mark', u'meter', u'nav', u'ol', u'output', u'p', u'pre', u'progress', u'q', u'rp', u'rt', u'ruby', u'samp', u'section', u'small', u'source', u'span', u'strong', u'sub', u'sup', u'table', u'tbody', u'td', u'tfoot', u'th', u'thead', u'time', u'title', u'tr', u'tt', u'u', u'ul', u'var', u'video', u'script']
        filter_settings.custom_attributes = [u'data-height', u'style']

        transaction.commit()

        from Products.CMFPlone.interfaces import IMarkupSchema
        markup_settings = getUtility(IRegistry).forInterface(IMarkupSchema, prefix='plone')
        markup_settings.allowed_types = ('text/html', 'text/x-web-markdown', 'text/x-web-textile')

        return "TinyMCE configuration and markdown applied"


class setupLDAPUPC(BrowserView):
    """ Configure LDAPUPC for Plone instance """

    def __call__(self):
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

                plugin.manage_activateInterfaces(['IAuthenticationPlugin',
                                                  'IGroupEnumerationPlugin',
                                                  'IGroupIntrospection',
                                                  'IGroupsPlugin',
                                                  'IRolesPlugin',
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


class setupLDAPExterns(BrowserView):
    """ Configure LDAPExterns for Plone instance """

    def __call__(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass
        portal = getSite()

        if 'branch' not in self.request.form:
            raise ValueError("Mandatory parameter 'branch' was not specified")
        else:
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
            api.portal.set_registry_record('base5.core.controlpanel.core.IBaseCoreControlPanelSettings.groups_query', groups_query)
            api.portal.set_registry_record('base5.core.controlpanel.core.IBaseCoreControlPanelSettings.user_groups_query', user_groups_query)
            return 'Done. groupOfUniqueNames in LDAP Controlpanel Search'


class setupLDAP(BrowserView):
    """ Configure basic LDAP for Plone instance """

    def __call__(self):
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

        users_base = f'ou=users,ou={branch_name},{base_dn}'
        groups_base = f'ou=groups,ou={branch_name},{base_dn}'
        bind_uid = f'cn={branch_admin_cn},ou={branch_name},{base_dn}'

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


class view_user_catalog(BrowserView):
    """ Rebuild the OMEGA13 repoze.catalog for user properties data """

    @json_response
    def __call__(self):
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

class reset_user_catalog(BrowserView):
    """ Reset the OMEGA13 repoze.catalog for user properties data.
    Add the force parameter to call correctly."""

    def __call__(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass

        from base5.core.utils import reset_user_catalog
        if 'force' in self.request.form:
            reset_user_catalog()
            return 'Done.'
        else:
            return 'Error, you have to add the force parameter'


class rebuild_user_catalog(BrowserView):
    """ Rebuild the OMEGA13 repoze.catalog for user properties data

For default, we use the mutable_properties (users who have entered into communities)

Path directo del plugin:
acl_users/plugins/manage_plugins?plugin_type=IPropertiesPlugin

En ACL_USERS / LDAP / Properties / Active Plugins ha de estar ordenado así:
  mutable_properties / auto_group / ldapaspb

But really, we use the most preferent plugin
If the most preferent plugin is:
   mutable_properties --> users who have entered into communities
   ldap --> users in LDAP  """

    def __call__(self):
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

        results = []
        maxclient, settings = getUtility(IMAXClient)()
        maxclient.setActor(settings.max_restricted_username)
        maxclient.setToken(settings.max_restricted_token)

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
                #Si el usuario existe en el MAX actualizamos el displayName si lo han cambiado
                #Si no existe en el MAX lo creamos
                try:
                    result = maxclient.people[user['id']].get()
                    if result['displayName'] != user['fullname']:
                        properties = dict(displayName=user['fullname'])
                        maxclient.people[user['id']].put(**properties)
                        logger.info(f'Update user in MAX: {user["id"]}')
                        results.append(f'Update user in MAX: {user["id"]}')
                except:
                    properties = dict(displayName=user['fullname'])
                    maxclient.people[user['id']].post(**properties)
                    logger.info(f'Create user in MAX: {user["id"]}')
                    results.append(f'Create user in MAX: {user["id"]}')
                add_user_to_catalog(user_obj, user)
            else:
                logger.info(f'No user found in user repository (LDAP) {user["id"]}')

            logger.info(f'Updated properties catalog for {user["id"]}')

        logger.info(f'Finish rebuild_user_catalog portal {portal}')

        return 'Done'


class UserMaxNotLDAP(BrowserView):
    """ Users in MAX not in LDAP.
        Vista per veure quins usuaris estan en el MAX i no al LDAP abans esborrar

        Path directo del plugin:
        acl_users/plugins/manage_plugins?plugin_type=IPropertiesPlugin

        En ACL_USERS / LDAP / Properties / Active Plugins ha de estar ordenado así:
        mutable_properties / auto_group / ldapexterns
    """

    def __call__(self):
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

        query = self.request.form.get('q', '')

        maxclient, settings = getUtility(IMAXClient)()
        maxclient.setActor(settings.max_restricted_username)
        maxclient.setToken(settings.max_restricted_token)

        # Todos los usuarios que estan en el MAX
        fulluserinfo = maxclient.people.get(qs={'limit': 0, 'username': query})

        # Usuarios admin que no podemos borrar
        admin_users = maxclient.admin.security.users()
        list_admin_users = []

        for user in admin_users:
            list_admin_users.append(str(user['username']))

        try:
            acl = pplugin._getLDAPUserFolder()
            for user in fulluserinfo:
                if str(user['username']) in list_admin_users:
                    pass
                else:
                    user_obj = acl.getUserById(user['username'])
                    if not user_obj:
                        logger.info(f'No user found in user repository (LDAP) {user["username"]}')
                        results.append(f'User for delete: {user["username"]}')


            logger.info(f'Finish users_max_not_ldap portal {portal}')
            results.append('Finish users_max_not_ldap')
            return '\n'.join([str(item) for item in results])
        except:
            logger.info('The order to the plugins in En ACL_USERS / LDAP / Properties / Active Plugins : mutable_properties / auto_group / ldapaspb')
            results.append('The order to the plugins in En ACL_USERS / LDAP / Properties / Active Plugins : mutable_properties / auto_group / ldapaspb')
            return 'Error: ' + '\n'.join([str(item) for item in results])


class DeleteUserMaxNotLDAP(BrowserView):
    """ Delete users in MAX not in LDAP.
        Vista per esborrar del cataleg i que no apareguin al directori
        els usuaris que no estan al LDAP

        Path directo del plugin:
        acl_users/plugins/manage_plugins?plugin_type=IPropertiesPlugin

        En ACL_USERS / LDAP / Properties / Active Plugins ha de estar ordenado así:
        mutable_properties / auto_group / ldapexterns
    """

    def __call__(self):
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

        query = self.request.form.get('q', '')

        maxclient, settings = getUtility(IMAXClient)()
        maxclient.setActor(settings.max_restricted_username)
        maxclient.setToken(settings.max_restricted_token)

        # Todos los usuarios que estan en el MAX
        fulluserinfo = maxclient.people.get(qs={'limit': 0, 'username': query})

        # Usuarios admin que no podemos borrar
        admin_users = maxclient.admin.security.users()
        list_admin_users = []

        for user in admin_users:
            list_admin_users.append(str(user['username']))

        try:
            acl = pplugin._getLDAPUserFolder()

            for user in fulluserinfo:
                if str(user['username']) in list_admin_users:
                    pass
                else:
                    user_obj = acl.getUserById(user['username'])
                    if not user_obj:
                        logger.info(f'No user found in user repository (LDAP) {user["username"]}')
                        deleteMembers(self, user['username'])
                        member_id = str(user['username'])
                        remove_user_from_catalog(member_id.lower())
                        logger.info(f'Eliminat usuari {member_id.lower()} del catalog.')
                        pc = api.portal.get_tool(name='portal_catalog')

                        communities_subscription = maxclient.people[member_id].subscriptions.get()

                        if communities_subscription != []:

                            for num, community_subscription in enumerate(communities_subscription):
                                community = pc.unrestrictedSearchResults(portal_type="ulearn.community", community_hash=community_subscription['hash'])
                                try:
                                    obj = community[0]._unrestrictedGetObject()
                                    logger.info(f'Processant {num} de {len(communities_subscription)}. Comunitat {obj}')
                                    gwuuid = IGWUUID(obj).get()
                                    portal = api.portal.get()

                                    communities_acl = get_or_initialize_annotation('communities_acl')
                                    record = next((r for r in communities_acl.values() if r.get('gwuuid') == gwuuid), None)

                                    if record:
                                        acl = record.get('acl')
                                        user_record = next((user for user in acl.get('users', []) if user.get('id') == str(member_id)), None)

                                        if user_record:
                                            acl['users'].remove(user_record)
                                            record['acl'] = acl

                                            adapter = obj.adapted()
                                            adapter.remove_acl_atomic(member_id)
                                            adapter.set_plone_permissions(adapter.get_acl())

                                            adapter.update_hub_subscriptions()

                                            if obj.notify_activity_via_mail and obj.type_notify == 'Automatic':
                                                adapter.update_mails_users(obj, acl)

                                except:
                                    continue

                        # Lo borramos del MAX
                        maxclient.people[member_id].delete()

                        logger.info(f'User delete {user["username"]}')
                        results.append(f'User delete: {user["username"]}')

            logger.info(f'Finish delete_users_max_not_ldap portal {portal}')
            results.append('Finish delete_users_max_not_ldap')
            return '\n'.join([str(item) for item in results])
        except:
            logger.info('The order to the plugins in En ACL_USERS / LDAP / Properties / Active Plugins : mutable_properties / auto_group / ldapaspb')
            results.append('The order to the plugins in En ACL_USERS / LDAP / Properties / Active Plugins : mutable_properties / auto_group / ldapaspb')
            return 'Error: ' + '\n'.join([str(item) for item in results])


class DeleteUserPropertiesCatalog(BrowserView):
    """ Delete users in catalog not in LDAP.
        Vista per esborrar del cataleg i que no apareguin al directori
        els usuaris que no estan al LDAP

Path directo del plugin:
acl_users/plugins/manage_plugins?plugin_type=IPropertiesPlugin

En ACL_USERS / LDAP / Properties / Active Plugins ha de estar ordenado así:
  mutable_properties / auto_group / ldapaspb """

    def __call__(self):
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
                    logger.info('No user found in user repository (LDAP) {}'.format(record[1].attrs['id']))
                    soup.__delitem__(record[1])
                    logger.info('User delete soup {}'.format(record[1].attrs['id']))
                    results.append('User delete soup: {}'.format(record[1].attrs['id']))

            logger.info('Finish delete_user_catalog portal {}'.format(portal))
            results.append('Finish delete_user_catalog')
            return '\n'.join([str(item) for item in results])
        except:
            logger.info('The order to the plugins in En ACL_USERS / LDAP / Properties / Active Plugins : mutable_properties / auto_group / ldapaspb')
            results.append('The order to the plugins in En ACL_USERS / LDAP / Properties / Active Plugins : mutable_properties / auto_group / ldapaspb')
            return 'Error: ' + '\n'.join([str(item) for item in results])



class delete_local_roles(BrowserView):
    """ Delete local roles of specified members.
        Vista per esborrar els permisos del site dels usuaris esborrats
    """

    def __call__(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass

        portal = api.portal.get()
        users_delete_local_roles = get_or_initialize_annotation('users_delete_local_roles')
        users_items = [r for r in users_delete_local_roles.items()]
        for key, value in users_items:
            member_id = value.get('id_username')
            if member_id:
                if isinstance(member_id, str):
                    member_ids = (member_id,)
                    member_ids = list(member_ids)

                mtool = api.portal.get_tool(name='portal_membership')
                # Delete members' local roles.
                mtool.deleteLocalRoles(getUtility(ISiteRoot), member_ids,
                                   reindex=1, recursive=1)
                logger.info(f'Eliminat usuari {member_id} del local roles.')

                del users_delete_local_roles[key]
                logger.info(f'Eliminat usuari {member_id} del soup.')

        logger.info(f'Finish delete_local_roles portal {portal}')

        return 'Done'


class users_to_delete_local_roles(BrowserView):
    """ Users to delete local roles of specified members.
        Vista per veure els usuaris que estan esborrats pero pendents esborrar permisos site
    """

    def __call__(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass

        results = []
        try:
            portal = api.portal.get()
            users_delete_local_roles = get_or_initialize_annotation('users_delete_local_roles')
            users = [r for r in users_delete_local_roles.items()]

            for key, value in users:
                member_id = value.get('id_username')
                if member_id:
                    results.append(f'User to delete: {member_id}')
                    logger.info(f'User to delete: {member_id}')

            logger.info(f'Finish users_to_delete_local_roles portal {portal}')
            results.append('Finish users_to_delete_local_roles')
            return '\n'.join([str(item) for item in results])
        except:
            logger.info('Except Users to delete local roles')
            results.append('Except Users to delete local roles')
            return 'Error: ' + '\n'.join([str(item) for item in results])


class rebuild_users_portrait(BrowserView):
    """ Users portrait
        Vista per actualitzar soup dels usuaris per dir si tenen la foto canviada True o la de per defecte False
    """

    def __call__(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass
        portal = api.portal.get()
        users_portrait = get_or_initialize_annotation('users_portrait')
        plugins = portal.acl_users.plugins.listPlugins(IPropertiesPlugin)
        # We use the most preferent plugin
        # If the most preferent plugin is:
        #    mutable_properties --> users who have entered into communities
        #    ldap --> users in LDAP
        pplugin = plugins[0][1]
        all_user_properties = pplugin.enumerateUsers()

        for user in all_user_properties:
            user_obj = api.user.get(user['id'])

            if user_obj:
                id = user['id']
                maxclient, settings = getUtility(IMAXClient)()
                foto = maxclient.people[id].avatar
                imageUrl = foto.uri + '/large'

                portrait = urllib.urlretrieve(imageUrl)

                scaled, mimetype = convertSquareImage(portrait[0])
                portrait = Image(id=id, file=scaled, title=id)

                # membertool = api.portal.get_tool(name='portal_memberdata')
                # membertool._setPortrait(portrait, str(id))
                # import transaction
                # transaction.commit()
                member_info = get_safe_member_by_id(id)
                if member_info.get('fullname', False) \
                   and member_info.get('fullname', False) != id \
                   and isinstance(portrait, Image) and portrait.size != 3566 and portrait.size != 6186:
                    portrait_user = True
                    # 3566 is the size of defaultUser.png I don't know how get image
                    # title. This behavior is reproduced in profile portlet. Ahora tambien 6186
                else:
                    portrait_user = False

                record = next((r for r in users_portrait.values() if r.get('id_username') == id), None)
                if record:
                    record['id_username'] = id
                    record['portrait'] = portrait_user
                else:
                    record = {
                        'id_username': id,
                        'portrait': portrait_user,
                    }
                    unique_key = str(uuid.uuid4())
                    users_portrait[unique_key] = record

            else:
                logger.info(f'No user found in user repository (LDAP) {user["id"]}')

            logger.info(f'Updated portrait user for {user["id"]}')

        logger.info(f'Finish rebuild_user_portrait portal {portal}')
        return 'Done'


class view_users_portrait(BrowserView):
    """ Users portrait
        Vista per veure soup dels usuaris per dir si tenen la foto canviada True o la de per defecte False
    """

    @json_response
    def __call__(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass
        users_portrait = get_or_initialize_annotation('users_portrait')

        result = {}
        for key, value in users_portrait.items():
            item = {attr_key: attr_value for attr_key, attr_value in value.items()}
            result[value.get('id_username')] = item

        return result
