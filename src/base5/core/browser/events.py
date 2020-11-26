# -*- coding: utf-8 -*-
from plone.app.contenttypes.browser.folder import FolderView
from plone.app.contenttypes.interfaces import IEvent
from plone.memoize.instance import memoize
from plone import api
from zope.i18nmessageid import MessageFactory

from base5.core import _
from base5.core.utils import abrevia
from ulearn5.core.hooks import packages_installed
from ulearn5.core.utils import getUserPytzTimezone

PLMF = MessageFactory('plonelocales')


class GridEventsView(FolderView):
    """ Grid view for events. """

    @property
    def no_items_message(self):
        """Translate custom message for no events in this folder."""
        return _(
            'description_no_events_in_folder',
            default=u'There are currently no events in this folder.'
        )

    def _query_events(self):
        """Get all events from this folder."""
        events = self.results(
            batch=True,
            object_provides=IEvent.__identifier__,
            sort_order='descending',
            sort_on='start',
        )
        return events

    @memoize
    def get_events(self):
        """Customize which properties we want to show in pt."""

        installed = packages_installed()
        if 'ulearn5.miranza' in installed:
            from ulearn5.miranza.patches import get_events as get_events_miranza
            return get_events_miranza(self)

        events = []
        ts = api.portal.get_tool(name='translation_service')
        results = self._query_events()
        timezone = getUserPytzTimezone()
        for event in results:
            description = abrevia(event.description, 100) if event.description else None
            start = event.start.astimezone(timezone)
            end = event.end.astimezone(timezone)
            location = event.location if event.location else None
            info = {'url': event.getURL(),
                    'firstday': start.day,
                    'firstmonth': PLMF(ts.month_msgid(start.month)),
                    'abbrfirstmonth': PLMF(ts.month_msgid(start.month)),
                    'firstyear': start.year,
                    'lastday': end.day,
                    'lastmonth': PLMF(ts.month_msgid(end.month)),
                    'abbrlastmonth': PLMF(ts.month_msgid(end.month)),
                    'lastyear': end.year,
                    'title': abrevia(event.title, 60),
                    'descr': description,
                    'location': location,
                    'timezone': event.timezone,
                    'showflip': location or description
                    }
            events.append(info)
        return events

    def dateType(self, event):
        """Select which type of text appears in circle."""
        startday = event['firstday']
        endday = event['lastday']
        startmonth = event['firstmonth']
        endmonth = event['lastmonth']
        startyear = event['firstyear']
        endyear = event['lastyear']
        if startmonth != endmonth or startyear != endyear:
            return 'difday_difmonth'
        elif startday != endday:
            return 'difday_samemonth'
        else:
            return 'sameday_samemonth'
