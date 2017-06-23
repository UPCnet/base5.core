from plone import api
from Products.CMFCore.utils import getToolByName


def pref_lang():
    """ Extracts the current language for the current user
    """
    portal = api.portal.get()
    lt = getToolByName(portal, 'portal_languages')
    return lt.getPreferredLanguage()
