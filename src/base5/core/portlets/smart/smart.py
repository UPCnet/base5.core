# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent

#from plone.app.collection.interfaces import ICollection
from plone import api
from plone.app.portlets.portlets import base
from plone.app.querystring.querybuilder import QueryBuilder
from plone.directives import form
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize import ram
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from time import time
from z3c.form import field
from zope import schema
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implements
from zope.schema.interfaces import ICollection

from base5.core import _
from base5.core.portlets.smart.renderers.interfaces import IPortletContainerRenderer
from base5.core.portlets.smart.renderers.interfaces import IPortletItemRenderer
from ulearn5.core.hooks import packages_installed

import random
import sys


class ISmart(IPortletDataProvider):
    """A portlet which renders the results of a collection object.
    """

    header = schema.TextLine(
        title=_("Portlet header"),
        description=_("Title of the rendered portlet"),
        required=True)

    show_header = schema.Bool(
        title=_('label_show_header', default='Show header'),
        description=_('Renders the header'),
        required=False,
        default=True
    )

    description = schema.TextLine(
        title=_("Portlet description"),
        description=_("Description of the portlet"),
        required=False)

    container_view = schema.Choice(
        title=_('label_container_view', default='Portlet view to use'),
        description=_("""Portlet view to use"""),
        vocabulary="base.portlet.smart.AvailablePortletContainerRenderers",
        required=True
    )

    query = schema.List(
        title=_('label_query', default='Search terms'),
        description=_("""Define the search terms for the items you want to
            list by choosing what to match on.
            The list of results will be dynamically updated"""),
        value_type=schema.Dict(value_type=schema.Field(),
                               key_type=schema.TextLine()),
        required=False
    )

    form.mode(sort_on='hidden')
    sort_on = schema.TextLine(
        title=_('label_sort_on', default='Sort on'),
        description=_("Sort the collection on this index"),
        required=False,
    )

    form.mode(sort_order='hidden')
    sort_order = schema.Bool(
        title=_('label_sort_reversed', default='Reversed order'),
        description=_('Sort the results in reversed order'),
        required=False,
    )

    sort_folderorder = schema.Bool(
        title=_('label_sort_folderorder', default='Order as in folder'),
        description=_('Override query sort order using folder order'),
        required=False,
    )

    limit = schema.Int(
        title=_("Limit"),
        description=_("Specify the maximum number of items to show in the "
                      "portlet. Leave this blank to show all items."),
        required=False)

    random = schema.Bool(
        title=_("Select random items"),
        description=_("If enabled, items will be selected randomly from the "
                      "collection, rather than based on its sort order."),
        required=True,
        default=False)

    more_link = schema.TextLine(
        title=_("Show more link"),
        description=_("Link to display in the footer, leave empty to hide it"),
        required=False)

    more_text = schema.TextLine(
        title=_("Show more link text"),
        description=_("Label the 'Show more link' defined avobe"),
        default='+',
        required=False)


class Assignment(base.Assignment):
    """
    Portlet assignment.
    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ISmart)

    header = ""
    query = None
    limit = None
    random = False

    def __init__(self, header="", show_header=True, sort_folderorder=False, sort_on="effective", sort_order=False, description='', query=None, limit=None, random=False, more_link="", more_text="+", container_view="li_container_render"):
        self.header = header
        self.description = description
        self.sort_on = sort_on
        self.sort_order = sort_order
        self.sort_folderorder = sort_folderorder
        self.limit = limit
        self.query = query
        self.random = random
        self.container_view = container_view
        self.more_link = more_link
        self.more_text = more_text
        self.show_header = show_header

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return self.header


class Renderer(base.Renderer):

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        self.plone_view = getMultiAdapter((self.context, self.request), name='plone')
        self.ptypes = api.portal.get_tool(name='portal_types')

    def render(self):
        renderer = getAdapter(self, IPortletContainerRenderer, name=self.data.container_view)
        return renderer()

    @property
    def available(self):
        return True
        return len(self.results())

    def css_class(self):
        header = self.data.header
        normalizer = getUtility(IIDNormalizer)
        return "portlet-smart-%s" % normalizer.normalize(header)

    @memoize
    def results(self):
        if self.data.random:
            return self._random_results()
        else:
            return self._standard_results()

    def getItemRenderer(self, item):
        args = dict(
            item=item,
            toLocalizedTime=self.plone_view.toLocalizedTime,
            cropText=self.plone_view.cropText)
        fti = self.ptypes.getTypeInfo(item.PortalType())
        module = fti.klass[:fti.klass.rfind('.')]
        klass = fti.klass[fti.klass.rfind('.') + 1:]
        dummy = getattr(sys.modules[module], klass)
        renderer = getAdapter(dummy(object), IPortletItemRenderer)
        return renderer(self, **args)

    def queryCatalog(self, limit):
        """
        """
        querybuilder = QueryBuilder(self, self.request)
        if not hasattr(self.data, 'sort_on'):
            self.data.sort_on = 'effective'
        if not hasattr(self.data, 'sort_order'):
            self.data.sort_order = False
        if not hasattr(self.data, 'sort_folderorder'):
            self.data.sort_folderorder = False

        sort_order = 'descending' if self.data.sort_order else 'ascending'
        sort_on = self.data.sort_on

        if self.data.sort_folderorder:
            sort_on = 'getObjPositionInParent'

        query = list(self.data.query)

        if ICollection.providedBy(self.context):
            query += self.context.query and self.context.query or []
            parent = aq_parent(aq_inner(self.context))
            if ICollection.providedBy(parent):
                query += parent.query and parent.query or []
        return querybuilder(query=query,
                            sort_on=sort_on,
                            sort_order=sort_order,
                            limit=limit)

    def _standard_results(self):
        results = []
        limit = self.data.limit
        if self.data.query:
            results = self.queryCatalog(limit=limit)
            if limit and limit > 0:
                results = results[:limit]
        return results

    def _random_results(self):
        # intentionally non-memoized
        results = []
        if self.data.query:
            results = self.queryCatalog()
            results = random.sample(results, self.data.limit)
        return results

    @ram.cache(lambda *args: time() // (60 * 60))
    def isUlearn(self):
        installed = packages_installed()
        if 'ulearn5.theme' in installed:
            return True
        return False


class AddForm(base.AddForm):

    schema = ISmart
    label = _("Add Query Portlet")
    description = _("This portlet displays a listing of items from a "
                    "Collection.")

    fields = field.Fields(ISmart)
    fields['sort_on'].mode = 'hidden'
    fields['sort_order'].mode = 'hidden'

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):

    schema = ISmart
    label = _("Edit Collection Portlet")
    description = _("This portlet displays a listing of items from a "
                    "Collection.")

    fields = field.Fields(ISmart)
    fields['sort_on'].mode = 'hidden'
    fields['sort_order'].mode = 'hidden'

    def extractData(self):
        data, errors = super(EditForm, self).extractData()
        data['sort_on'] = self.request.form.get('sort_on')
        data['sort_order'] = False if self.request.form.get('sort_order') is None else True
        return data, errors
