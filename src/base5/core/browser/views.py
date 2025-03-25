# -*- coding: utf-8 -*-
import uuid

from Acquisition import aq_inner
from base5.core import _
from base5.core.adapters import IFlash, IImportant, IOutOfList, IShowInApp
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from ulearn5.core.utils import get_or_initialize_annotation
from zope.component.hooks import getSite
from repoze.catalog.query import Eq
from souper.soup import get_soup
from souper.soup import Record

class gwToggleIsImportant(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        is_important = IImportant(context).is_important
        if is_important:
            IImportant(context).is_important = False
            confirm = _('L\'element s\'ha desmarcat com important')
        else:
            IImportant(context).is_important = True
            confirm = _('L\'element s\'ha marcat com important')

        IStatusMessage(self.request).addStatusMessage(confirm, type='info')
        self.request.response.redirect(self.context.absolute_url())


class gwToggleIsFlash(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        is_flash = IFlash(context).is_flash
        if is_flash:
            IFlash(context).is_flash = False
            confirm = _('L\'element s\'ha desmarcat com flash')
        else:
            IFlash(context).is_flash = True
            confirm = _('L\'element s\'ha marcat com flash')

        IStatusMessage(self.request).addStatusMessage(confirm, type='info')
        self.request.response.redirect(self.context.absolute_url())


class gwToggleIsOutoflist(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        is_outoflist = IOutOfList(context).is_outoflist
        if is_outoflist:
            IOutOfList(context).is_outoflist = False
            confirm = _('L\'element s\'ha desmarcat de la blacklist')
        else:
            IOutOfList(context).is_outoflist = True
            confirm = _('L\'element s\'ha marcat com a blacklist')

        IStatusMessage(self.request).addStatusMessage(confirm, type='info')
        self.request.response.redirect(self.context.absolute_url())


class gwToggleNewsInApp(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        is_inapp = IShowInApp(context).is_inapp
        if is_inapp:
            IShowInApp(context).is_inapp = False
            confirm = _('L\'element no es mostra a la App')
        else:
            IShowInApp(context).is_inapp = True
            confirm = _('L\'element es mostra a la App')

        IStatusMessage(self.request).addStatusMessage(confirm, type='info')
        self.request.response.redirect(self.context.absolute_url())


class gwToggleSubscribedTag(BrowserView):

    def __call__(self):
        portal = api.portal.get()
        current_user = api.user.get_current()
        userid = current_user.id
        tag = self.request.form['tag']

        soup_tags = get_soup('user_subscribed_tags', portal)
        exist = [r for r in soup_tags.query(Eq('id', userid))]

        if not exist:
            record = Record()
            record.attrs['id'] = userid
            record.attrs['tags'] = [tag]
            soup_tags.add(record)
        else:
            subscribed = [True for utag in exist[0].attrs['tags'] if utag == tag]
            if subscribed:
                exist[0].attrs['tags'].remove(tag)
            else:
                exist[0].attrs['tags'].append(tag)
        soup_tags.reindex()

        if IPloneSiteRoot.providedBy(self.context):
            self.request.response.redirect(self.context.absolute_url() + '/alltags')
        else:
            self.request.response.redirect(self.context.absolute_url())
