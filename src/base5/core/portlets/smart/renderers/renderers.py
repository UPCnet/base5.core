# -*- coding: utf-8 -*-
import re

from base5.core.portlets.smart.renderers import (PortletContainerRenderer,
                                                 PortletItemRenderer)
from base5.core.portlets.smart.renderers.interfaces import (
    IPortletContainerRenderer, IPortletItemRenderer)
from plone.app.contenttypes.interfaces import IImage
from plone.app.portlets.portlets.base import IPortletRenderer
from Products.CMFCore.interfaces import IContentish
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapter
from zope.interface import implementer

AUDIO_REGEX = re.compile(r'.mp3|.m4a|.acc|.f4a|.ogg|.oga|.mp4|.m4v|.f4v|.mov|.flv|.webm|.smil|.m3u8', re.IGNORECASE)


@implementer(IPortletContainerRenderer)
@adapter(IPortletRenderer)
class ListPortletContainerRenderer(PortletContainerRenderer):

    title = "View with items wrapped in ul > li"
    template = ViewPageTemplateFile('templates/container_li.pt')
    css_class = 'portlet-container-list'


@implementer(IPortletContainerRenderer)
@adapter(IPortletRenderer)
class DivPortletContainerRenderer(PortletContainerRenderer):

    title = "View with items wrapped in div > div"
    template = ViewPageTemplateFile('templates/container_div.pt')
    css_class = 'portlet-container-div'


@implementer(IPortletContainerRenderer)
@adapter(IPortletRenderer)
class CarouselPortletContainerRenderer(PortletContainerRenderer):

    title = "Carousel view"
    template = ViewPageTemplateFile('templates/container_carousel.pt')
    css_class = 'carousel-container-div'

    def getTitleIdPortlet(self):
        return self.portlet.data.header.replace(" ", "-")


@implementer(IPortletItemRenderer)
@adapter(IImage)
class ImagePortletItemRenderer(PortletItemRenderer):

    title = "Image view"
    template = ViewPageTemplateFile('templates/image.pt')
    css_class = 'carousel-image'


@implementer(IPortletItemRenderer)
@adapter(IContentish)
class DefaultPortletItemRenderer(PortletItemRenderer):

    template = ViewPageTemplateFile('templates/default.pt')
    css_class = 'contentish-item'
