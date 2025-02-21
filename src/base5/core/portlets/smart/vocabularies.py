# -*- coding: utf-8 -*-
from base5.core.portlets.smart.renderers.interfaces import \
    IPortletContainerRenderer
from plone.app.portlets.portlets.base import Renderer
from zope.component import getAdapters
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


@implementer(IVocabularyFactory)
class AvailablePortletContainerRenderers(object):
    """Vocabulary factory for workflow states.
    """

    def __call__(self, context):
        DummyRenderer = Renderer(context, None, None, None, None)
        renderers = [a for a in getAdapters((DummyRenderer,), IPortletContainerRenderer)]
        terms = [SimpleTerm(k, title=v.title) for k, v in renderers]
        return SimpleVocabulary(terms)


AvailablePortletContainerRenderersFactory = AvailablePortletContainerRenderers()
