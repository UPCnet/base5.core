# -*- coding: utf-8 -*-
import fnmatch

import unittest2 as unittest
from AccessControl import Unauthorized
from base5.core.testing import BASE5_CORE_INTEGRATION_TESTING
from plone import api
from plone.app.testing import (SITE_OWNER_NAME, TEST_USER_ID, TEST_USER_NAME,
                               applyProfile, login, logout, setRoles)
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from ulearn5.core.utils import get_or_initialize_annotation
from zope.component import getMultiAdapter, queryUtility


class TestOmega13(unittest.TestCase):

    layer = BASE5_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_directory_self_updates_on_user_creation(self):
        api.user.create(email='test@upcnet.es', username='testdirectory',
                        properties=dict(fullname='Test Directory User',
                                        location='Barcelona',
                                        email='test@upcnet.es'))
        user_properties = get_or_initialize_annotation('user_properties')
        record = next((r for r in user_properties.values() if r.get('username') == 'testdirectory'), None)
        self.assertEqual('test@upcnet.es', record.get('email'))
        record = next((r for r in user_properties.values() if fnmatch.fnmatch(r.get('fullname', ''), 'Test*')))
        self.assertEqual('Test Directory User', record.get('fullname'))

    def test_directory_self_updates_on_user_property_edit(self):
        api.user.create(email='test@upcnet.es', username='testdirectory',
                        properties=dict(fullname='Test Directory User',
                                        location='Barcelona',
                                        email='test@upcnet.es'))
        user = api.user.get(username='testdirectory')
        user.setMemberProperties(mapping={'location': 'Barcelona', 'telefon': '654321'})
        user_properties = get_or_initialize_annotation('user_properties')
        record = next((r for r in user_properties.values() if r.get('username') == 'testdirectory'), None)
        self.assertEqual('test@upcnet.es', record.get('email'))
        self.assertEqual('Barcelona', record.get('location'))

    def test_full_directory_update(self):
        api.user.create(email='test@upcnet.es', username='testdirectory',
                        properties=dict(fullname='Test Directory User',
                                        location='Barcelona',
                                        email='test@upcnet.es'))
        api.user.create(email='test@upcnet.es', username='testdirectory2',
                        properties=dict(fullname='Test Directory User',
                                        location='Barcelona',
                                        email='test@upcnet.es'))

        view = getMultiAdapter((self.portal, self.request), name='rebuild_user_catalog')
        view.render()

    def test_directory_self_updates_on_user_creation_with_unicode(self):
        api.user.create(email='test@upcnet.es', username='testdirectory',
                        properties=dict(fullname='Víctor',
                                        location='Barcelona',
                                        email='test@upcnet.es'))
        user_properties = get_or_initialize_annotation('user_properties')
        record = next((r for r in user_properties.values() if r.get('username') == 'testdirectory'), None)
        self.assertEqual('test@upcnet.es', record.get('email'))
        record = next((r for r in user_properties.values() if fnmatch.fnmatch(r.get('fullname', ''), 'Ví*')))
        self.assertEqual('Víctor', record.get('fullname'))

