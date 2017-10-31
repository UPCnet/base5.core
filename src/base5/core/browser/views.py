# -*- coding: utf-8 -*-
from five import grok
from zope.interface import Interface
from base5.core.utils import genweb_config
from base5.core.interfaces import IBase5CoreLayer


class GWConfig(grok.View):
    grok.context(Interface)
    grok.layer(IBase5CoreLayer)

    def render(self):
        return genweb_config()
