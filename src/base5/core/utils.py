# -*- coding: utf-8 -*-
import io
import json
import logging
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import uuid
from io import StringIO
from time import time

import PIL
import requests
from AccessControl import getSecurityManager
from base5.core import HAS_PAM, IAMULEARN
from base5.core.controlpanel.core import IBaseCoreControlPanelSettings
from base5.core.directory import METADATA_USER_ATTRS
from bs4 import BeautifulSoup
from mrs5.max.utilities import IMAXClient
from OFS.Image import Image
from PIL import ImageOps
from plone import api
from plone.registry.interfaces import IRegistry
from Products.PlonePAS.plugins.ufactory import PloneUser
from Products.PlonePAS.tools.memberdata import MemberData
from souper.interfaces import ICatalogFactory
from ulearn5.core.utils import get_or_initialize_annotation
from zope.component import getUtilitiesFor, getUtility, queryUtility
from zope.component.hooks import getSite
from zope.i18nmessageid import MessageFactory

logger = logging.getLogger(__name__)

PLMF = MessageFactory('plonelocales')

if HAS_PAM:
    from plone.app.multilingual.interfaces import ITranslationManager


def base_config():
    """ Funcio que retorna les configuracions del controlpanel """
    registry = queryUtility(IRegistry)
    return registry.forInterface(IBaseCoreControlPanelSettings)


def havePermissionAtRoot():
    """Funcio que retorna si es Editor a l'arrel"""
    proot = portal()
    pm = api.portal.get_tool(name='portal_membership')
    sm = getSecurityManager()
    user = pm.getAuthenticatedMember()

    return sm.checkPermission('Modify portal content', proot) or \
        ('Manager' in user.getRoles()) or \
        ('Site Administrator' in user.getRoles())
    # WebMaster used to have permission here, but not anymore since uLearn
    # makes use of it
    # ('WebMaster' in user.getRoles()) or \


def portal_url():
    """Get the Plone portal URL out of thin air without importing fancy
       interfaces and doing multi adapter lookups.
    """
    return portal().absolute_url()


def portal():
    """Get the Plone portal object out of thin air without importing fancy
       interfaces and doing multi adapter lookups.
    """
    return getSite()


def abrevia(summary, sumlenght):
    """ Retalla contingut de cadenes
    """
    bb = ''

    if sumlenght < len(summary):
        bb = summary[:sumlenght]

        lastspace = bb.rfind(' ')
        cutter = lastspace
        precut = bb[0:cutter]

        if precut.count('<b>') > precut.count('</b>'):
            cutter = summary.find('</b>', lastspace) + 4
        elif precut.count('<strong>') > precut.count('</strong>'):
            cutter = summary.find('</strong>', lastspace) + 9
        bb = summary[0:cutter]

        if bb.count('<p') > precut.count('</p'):
            bb += '...</p>'
        else:
            bb = bb + '...'
    else:
        bb = summary

    try:
        return BeautifulSoup(bb.decode('utf-8', 'ignore')).prettify()
    except:
        return BeautifulSoup(bb).prettify()


def abreviaPlainText(summary, sumlenght):
    """ Retalla contingut de cadenes
    """
    bb = ''

    if sumlenght < len(summary):
        bb = summary[:sumlenght]

        lastspace = bb.rfind(' ')
        bb = bb[0:lastspace]
    else:
        bb = summary

    return bb


def pref_lang():
    """ Extracts the current language for the current user. """
    lt = api.portal.get_tool(name='portal_languages')
    return lt.getPreferredLanguage()


def link_translations(items):
    """
        Links the translations with the declared items with the form:
        [(obj1, lang1), (obj2, lang2), ...] assuming that the first element
        is the 'canonical' (in PAM there is no such thing).
    """
    # Grab the first item object and get its canonical handler
    canonical = ITranslationManager(items[0][0])

    for obj, language in items:
        if not canonical.has_translation(language):
            canonical.register_translation(language, obj)


def get_safe_member_by_id(username):
    """Gets user info from the repoze.catalog based user properties catalog.
       This is a safe implementation for getMemberById portal_membership to
       avoid useless searches to the LDAP server. It gets only exact matches (as
       the original does) and returns a dict. It DOES NOT return a Member
       object.
    """
    user_properties = get_or_initialize_annotation('user_properties')
    username = username.lower()
    record = next((r for r in user_properties.values() if r.get('id') == username), None)
    if record:
        properties = {}
        for key, value in record.items():
            if value:
                properties[key] = value

        if 'fullname' not in properties:
            properties['fullname'] = ''
        
        return properties
    else:
        # No such member: removed?  We return something useful anyway.
        return {'username': username, 'description': '', 'language': '',
                'home_page': '', 'name_or_id': username, 'location': '',
                'fullname': ''}


def get_all_user_properties(user):
    """
        Returns a mapping with all the defined user profile properties and its values.

        The properties list includes all properties defined on any profile extension that
        is currently registered. For each of this properties, the use object is queried to
        retrieve the value. This may result in a empty value if that property is not set, or
        the value of the property provided by any properties PAS plugin.

        NOTE: Mapped LDAP atrributes will be retrieved and returned on this mapping if any.

    """
    user_properties_utility = getUtility(ICatalogFactory, name='user_properties')
    attributes = user_properties_utility.properties + METADATA_USER_ATTRS

    try:
        extender_name = api.portal.get_registry_record('base5.core.controlpanel.core.IBaseCoreControlPanelSettings.user_properties_extender')
    except:
        extender_name = ''

    if extender_name:
        if extender_name in [a[0] for a in getUtilitiesFor(ICatalogFactory)]:
            extended_user_properties_utility = getUtility(ICatalogFactory, name=extender_name)
            #attributes_antiguo = attributes + extended_user_properties_utility.properties
            attributes.extend([element for element in extended_user_properties_utility.properties if element not in attributes])
    mapping = {}
    for attr in attributes:
        # OJO revisar este if mas adelante, no estaba en plone4
        if attr != 'username':
            try:
                value = user.getProperty(attr)
                if isinstance(value, str) or isinstance(value, bool) or isinstance(value, list) or isinstance(value, tuple):
                    mapping.update({attr: value})
            except:
                portal = api.portal.get()
                logger.error("ERROR PROPERTY {attr} in USER_PROPERTIES {extender_name} ALL_ATTRIBUTES {attributes} EXTENDED_PROPERTIES {extended_user_properties_utility.properties} PORTAL {portal}")
                pass

    return mapping


def remove_user_from_catalog(username):
    user_properties = get_or_initialize_annotation('user_properties')
    record_key, record = next(
        ((k, v) for k, v in user_properties.items() if v.get('id') == username), 
        (None, None)
    )
    if record_key is not None:
        del user_properties[record_key]

    if IAMULEARN:
        extender_name = api.portal.get_registry_record('base5.core.controlpanel.core.IBaseCoreControlPanelSettings.user_properties_extender')
        extended_soup = get_or_initialize_annotation(extender_name)
        record_key, record = next(
            ((k, v) for k, v in user_properties.items() if v.get('id') == username),
            (None, None)
        )

        if record_key is not None:
            del extended_soup[record_key]


def add_user_to_catalog(user, properties={}, notlegit=False, overwrite=False):
    """
    Adds a user to the user catalog.

    Se puede llamar con:
      - un usuario envuelto en MemberData,
      - un PloneUser,
      - o un string (username).

    Si no se pasan propiedades, se crea un registro básico.
    'notlegit' indica que el usuario se añade en modo "no legítimo" (sin searchable_text).
    'overwrite' indica si se deben sobrescribir valores existentes.
    """
    user_properties = get_or_initialize_annotation('user_properties')
    
    if isinstance(user, MemberData):
        username = user.getUserName()
    elif isinstance(user, PloneUser):
        username = user.getUserName()
    else:
        username = user
    username = username.lower()

    record = next((r for r in user_properties.values() if r.get('id') == username), None)
    user_properties_utility = getUtility(ICatalogFactory, name='user_properties')
    
    if record:
        # Just in case that a user became a legit one and previous was a nonlegit
        record['notlegit'] = False
    else:
        # If the user do not exist, and the notlegit is set (created by other
        # means, e.g. a test or ACL) then set notlegit to True This is because
        # in non legit mode, maybe existing legit users got unaffected by it
        record = {}
        if notlegit:
            record['notlegit'] = True
        unique_key = str(uuid.uuid4())
        user_properties[unique_key] = record

    record['username'] = username
    record['id'] = username

    if properties:
        for attr in user_properties_utility.properties + METADATA_USER_ATTRS:
            has_prop_def = attr in properties
            prop_empty = (record.get(attr, '') == '')
            if has_prop_def:
                if record.get(attr, '') != properties[attr]:
                    property_different_value = True
                else:
                    property_different_value = False
            else:
                property_different_value = False

            if has_prop_def and (prop_empty or overwrite or property_different_value):
                if isinstance(properties[attr], str):
                    record[attr] = properties[attr]
                elif isinstance(properties[attr], bool):
                    record[attr] = str(properties[attr])
                else:
                    record[attr] = properties[attr]

    # If notlegit mode, then return without setting the 'searchable_text' This
    # is because in non legit mode, maybe existing legit users got unaffected by it
    if notlegit:
        return

    # Build the searchable_text field for wildcard searchs
    record['searchable_text'] = ''
    for key in user_properties_utility.properties:
        if record.get(key, False) and 'check_' not in key:
            checkKey = 'check_' + key
            hasCheck = checkKey in record
            if (not hasCheck) or (hasCheck and record.get(checkKey) != 'False'):
                normalized = unicodedata.normalize('NFKD', record.get(key))
                normalized_ascii = normalized.encode('ascii', errors='ignore').decode('ascii')
                record['searchable_text'] += normalized_ascii + ' '

    # If uLearn is present, then lookup for a customized set of fields and its
    # related soup. The soup has the form 'user_properties_<client_name>'. This
    # feature is currently restricted to uLearn but could be easily backported
    # to Base. The setting that makes the extension available lives in:
    # 'base5.core.controlpanel.core.IBaseCoreControlPanelSettings.user_properties_extender'
    if IAMULEARN:
        extender_name = api.portal.get_registry_record(
            'base5.core.controlpanel.core.IBaseCoreControlPanelSettings.user_properties_extender'
        )
        # Make sure that, in fact we have such a extender in place
        if extender_name in [a[0] for a in getUtilitiesFor(ICatalogFactory)]:
            extended_user_properties = get_or_initialize_annotation(extender_name)
            extended_record = next((r for r in extended_user_properties.values() if r.get('id') == username), None)
            extended_user_properties_utility = getUtility(ICatalogFactory, name=extender_name)
            
            if not extended_record:
                extended_record = {}
                unique_key_ext = str(uuid.uuid4())
                extended_user_properties[unique_key_ext] = extended_record

            extended_record['username'] = username
            extended_record['id'] = username

            if properties:
                for attr in extended_user_properties_utility.properties:
                    has_prop_def = attr in properties
                    prop_empty = (extended_record.get(attr, '') == '')
                    if has_prop_def:
                        if extended_record.get(attr, '') != properties[attr]:
                            property_different_value = True
                        else:
                            property_different_value = False
                    else:
                        property_different_value = False
                    
                    # Only update it if user has already not property set or it's empty
                    if has_prop_def and (prop_empty or overwrite or property_different_value):
                        if isinstance(properties[attr], str):
                            extended_record[attr] = properties[attr]
                        elif isinstance(properties[attr], bool):
                            extended_record[attr] = str(properties[attr])
                        else:
                            extended_record[attr] = properties[attr]


            # Update the searchable_text of the standard user record field with
            # the ones in the extended catalog
            record['searchable_text'] = ''
            if hasattr(extended_user_properties_utility, 'public_properties'):
                for key in extended_user_properties_utility.public_properties:
                    if extended_record.get(key, False) and 'check_' not in key:
                        checkKey = 'check_' + key
                        hasCheck = checkKey in extended_record
                        if (not hasCheck) or (hasCheck and extended_record.get(checkKey) != 'False'):
                            value = extended_record.get(key)
                            if isinstance(value, (list, tuple)):
                                value = ' '.join(value)
                            if isinstance(value, str) and value.startswith('[[') and value.endswith(']]'):
                                try:
                                    value_list = json.loads(value)
                                    if value_list:
                                        value = ' '.join(value_list[0])
                                except Exception:
                                    pass
                            record['searchable_text'] += ' ' + value
            else:
                for key in extended_user_properties_utility.properties:
                    if extended_record.get(key, False) and 'check_' not in key:
                        checkKey = 'check_' + key
                        hasCheck = checkKey in extended_record
                        if (not hasCheck) or (hasCheck and extended_record.get(checkKey) != 'False'):
                            normalized = unicodedata.normalize('NFKD', extended_record.get(key))
                            normalized_ascii = normalized.encode('ascii', errors='ignore').decode('ascii')
                            record['searchable_text'] += ' ' + normalized_ascii

            # Save for free the extended properties in the main user_properties soup
            # for easy access with one query
            if properties:
                for attr in extended_user_properties_utility.properties:
                    has_prop_def = attr in properties
                    prop_empty = (record.get(attr, '') == '')
                    if has_prop_def:
                        if record.get(attr, '') != properties[attr]:
                            property_different_value = True
                        else:
                            property_different_value = False
                    else:
                        property_different_value = False

                    # Only update it if user has already not property set or it's empty
                    if has_prop_def and (prop_empty or overwrite or property_different_value):
                        if isinstance(properties[attr], str):
                            record[attr] = properties[attr]
                        elif isinstance(properties[attr], bool):
                            record[attr] = str(properties[attr])
                        else:
                            record[attr] = properties[attr]




def reset_user_catalog():
    user_properties = get_or_initialize_annotation('user_properties')
    user_properties.clear()


def reset_group_catalog():
    ldap_groups = get_or_initialize_annotation('ldap_groups')
    ldap_groups.clear()

def json_response(func):
    """ Decorator to transform the result of the decorated function to json.
        Expect a list (collection) that it's returned as is with response 200 or
        a dict with 'data' and 'status_code' as keys that gets extracted and
        applied the response.
    """
    def decorator(*args, **kwargs):
        instance = args[0]
        request = getattr(instance, 'request', None)
        request.response.setHeader(
            'Content-Type',
            'application/json; charset=utf-8'
        )
        result = func(*args, **kwargs)
        if isinstance(result, list):
            request.response.setStatus(200)
            return json.dumps(result, indent=2, sort_keys=True)
        else:
            request.response.setStatus(result.get('status_code', 200))
            return json.dumps(result.get('data', result), indent=2, sort_keys=True)

    return decorator


def convertSquareImage(image_file):
    CONVERT_SIZE = (250, 250)
    try:
        image = PIL.Image.open(image_file)
    except:
        portrait_url = portal_url() + '/++theme++ulearn5/assets/images/defaultUser.png'
        imgData = requests.get(portrait_url).content
        image = PIL.Image.open(io.BytesIO(imgData))
        image.filename = 'defaultUser'

    format = image.format
    mimetype = 'image/%s' % format.lower()

    result = ImageOps.fit(image, CONVERT_SIZE, method=PIL.Image.ANTIALIAS, centering=(0.5, 0.5))

    # Bypass CMYK problem in conversion
    if result.mode not in ["1", "L", "P", "RGB", "RGBA"]:
        result = result.convert("RGB")

    new_file = StringIO()
    result.save(new_file, format, quality=88)
    new_file.seek(0)

    return new_file, mimetype

def add_portrait_user(user):
    """ Esta función le pide al max la foto de perfil del usuario
        la añade al portrait de plone y guarda en un soup si es la de por defecto o no
    """
    id = user.id
    maxclient, settings = getUtility(IMAXClient)()
    foto = maxclient.people[id].avatar
    imageUrl = foto.uri + '/large'

    portrait = urllib.request.urlretrieve(imageUrl)

    scaled, mimetype = convertSquareImage(portrait[0])
    portrait = Image(id=id, file=scaled, title=id)

    portal = api.portal.get()
    membertool = api.portal.get_tool(name='portal_memberdata')
    membertool._setPortrait(portrait, str(id))
    import transaction
    transaction.commit()

    member_info = get_safe_member_by_id(id)
    if member_info.get('fullname', False) \
       and member_info.get('fullname', False) != id \
       and isinstance(portrait, Image) and portrait.size != 3566 and portrait.size != 6186:
        portrait_user = True
        # 3566 is the size of defaultUser.png I don't know how get image
        # title. This behavior is reproduced in profile portlet. Ahora tambien 6186
    else:
        portrait_user = False

    users_portrait = get_or_initialize_annotation('users_portrait')
    record = next((r for r in users_portrait.values() if r.get('id_username') == id), None)
    if record:
        record['id_username'] = id
        record['portrait'] = portrait_user
    else:
        record = {
            'id_username': id,
            'portrait': portrait_user
        }
        unique_key = str(uuid.uuid4())
        users_portrait[unique_key] = record
