# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from elasticsearch import Elasticsearch
from plone import api
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import implementer

class IElasticSearch(Interface):
    """ Marker for ElasticSearch global utility """


@implementer(IElasticSearch)
class ElasticSearch(object):

    def __init__(self):
        self._conn = None

    def __call__(self):
        return self.connection

    def create_new_connection(self):
        self.es_url = api.portal.get_registry_record('base5.core.controlpanel.core.IBaseCoreControlPanelSettings.elasticsearch')
        if (api.portal.get_registry_record('base5.core.controlpanel.core.IBaseCoreControlPanelSettings.elasticsearch') != 'localhost'):
            self._conn = Elasticsearch(self.es_url)

    @property
    def connection(self):
        if self._conn is None:
            self.create_new_connection()
        return self._conn


class ReloadESConfig(BrowserView):
    """ Convenience view for faster debugging. Needs to be manager. """

    def __call__(self):
        es = getUtility(IElasticSearch)
        es.reload = True
