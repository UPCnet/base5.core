from five import grok
from plone import api
from Products.PlonePAS.interfaces.events import IUserInitialLoginInEvent
from Products.PluggableAuthService.interfaces.authservice import IPropertiedUser
from Products.PluggableAuthService.interfaces.events import IPrincipalCreatedEvent
from Products.PluggableAuthService.interfaces.events import IPropertiesUpdatedEvent
from Products.PluggableAuthService.interfaces.events import IUserLoggedInEvent

from base5.core.utils import get_all_user_properties
from base5.core.utils import add_user_to_catalog
from ulearn5.core.hooks import packages_installed
from base5.core.utils import add_portrait_user

@grok.subscribe(IPropertiedUser, IPrincipalCreatedEvent)
def create_user_hook(user, event):
    """ This subscriber hooks on user creation and adds user properties to the
        soup-based catalog for later searches
    """
    add_user_to_catalog(user)


@grok.subscribe(IPropertiedUser, IPropertiesUpdatedEvent)
def update_user_properties_hook(user, event):
    """ This subscriber hooks on user creation and adds user properties to the
        soup-based catalog for later searches
    """
    installed = packages_installed()
    if 'ulearn5.enginyersbcn' not in installed:
        add_user_to_catalog(user, event.properties, overwrite=True)


@grok.subscribe(IUserLoggedInEvent)
def UpdateUserPropertiesOnLogin(event):
    user = api.user.get_current()
    try:
        installed = packages_installed()
        if 'ulearn5.medichem' in installed:
            # from ulearn5.medichem.overrides import get_all_user_properties_medichem
            # properties = get_all_user_properties_medichem(user)
            # add_portrait_user(user)
            pass
        else:
            properties = get_all_user_properties(user)
            add_user_to_catalog(user, properties, overwrite=True)
            #Por ahora comentamos el modificar la imagen en el login porque da conflict error en el ZEO si entran a la vez
            #add_portrait_user(user)
    except:
        # To avoid testing test_functional code, since the
        # test_user doesn't have properties and stops the tests.
        pass

@grok.subscribe(IUserInitialLoginInEvent)
def UpdateUserPropertiesOnFirstLogin(event):
    user = api.user.get_current()
    if hasattr(user, 'visible_userprofile_portlet'):
        user.setMemberProperties({'visible_userprofile_portlet': True})
    try:
        installed = packages_installed()
        if 'ulearn5.medichem' in installed:
            # from ulearn5.medichem.overrides import get_all_user_properties_medichem
            # properties = get_all_user_properties_medichem(user)
            pass
        else:
            properties = get_all_user_properties(user)
        for key, value in properties.iteritems():
            if 'check_' in key:
                user.setMemberProperties({key: True})
    except:
        # To avoid testing test_functional code, since the
        # test_user doesn't have properties and stops the tests.
        pass
