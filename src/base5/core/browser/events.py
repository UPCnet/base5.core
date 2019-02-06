# -*- coding: utf-8 -*-
from Acquisition import aq_base
from Acquisition import aq_inner
from base5.core.utils import abrevia
from base5.core.utils import pref_lang
from plone.app.contenttypes.browser.folder import FolderView
from plone.app.contenttypes.interfaces import IEvent
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as pmf
from Products.CMFPlone.PloneBatch import Batch
from zope.i18nmessageid import MessageFactory


PLMF = MessageFactory('plonelocales')


class GridEventsView(FolderView):
    """ Grid view for events. """

    @property
    def no_items_message(self):
        return pmf(
            'description_no_events_in_folder',
            default=u'There are currently no events in this folder.'
        )

    def _query_events(self):
        """Get all events from this folder."""
        events = self.results(
            batch=True,
            object_provides=IEvent.__identifier__,
            sort_on='getObjPositionInParent',
        )
        return events

    @memoize
    def get_events(self):
        events = []
        ts = getToolByName(self.context, 'translation_service')
        results = self._query_events()
        for event in results:
            info = {'url': event.getURL(),
                    'firstday': event.start.day,
                    'firstmonth': PLMF(ts.month_msgid(event.start.month)),
                    'abbrfirstmonth': PLMF(ts.month_msgid(event.start.month)),
                    'lastday': event.end.day,
                    'lastmonth': PLMF(ts.month_msgid(event.end.month)),
                    'abbrlastmonth': PLMF(ts.month_msgid(event.end.month)),
                    'connector': ' to ' if pref_lang() == 'en' else ' a ',
                    'title': event.title,
                    'descr': abrevia(event.description) if event.description else ""
                    }
            events.append(info)
        return events

    def dateType(self, event):
        startday = event['firstday']
        endday = event['lastday']
        startmonth = event['firstmonth']
        endmonth = event['lastmonth']
        if startmonth != endmonth:
            return 'difday_difmonth'
        elif startday != endday:
            return 'difday_samemonth'
        else:
            return 'sameday_samemonth'
