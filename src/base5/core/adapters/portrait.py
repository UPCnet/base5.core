# -*- coding: utf-8 -*-
from OFS.Image import Image
from plone import api
from Products.PlonePAS.interfaces.membership import IMembershipTool
from Products.PlonePAS.utils import scale_image
from zope.component import adapter
from zope.interface import Interface, implementer


class IPortraitUploadAdapter(Interface):
    """ The marker interface for the portrait upload adapter used for implement
        special actions after upload. The idea is to have a default (core)
        action and then other that override the default one using IBrowserLayer.
    """

@implementer(IPortraitUploadAdapter)
@adapter(IMembershipTool, Interface)
class PortraitUploadAdapter(object):
    """ Default adapter for portrait custom actions """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, portrait, safe_id):
        if portrait and portrait.filename:
            scaled, mimetype = scale_image(portrait)
            portrait = Image(id=safe_id, file=scaled, title='')
            membertool = api.portal.get_tool(name='portal_memberdata')
            membertool._setPortrait(portrait, safe_id)
