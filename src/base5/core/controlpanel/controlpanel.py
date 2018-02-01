# -*- coding: utf-8 -*-
from plone import api
from z3c.form import button
from zope.component.hooks import getSite
from zope.component import getAdapter
from zope.interface import alsoProvides

from plone.app.registry.browser import controlpanel
from plone.dexterity.utils import createContentInContainer

from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName

from base5.core.controlpanel.interface import IGenwebControlPanelSettings
from base5.core import _
from base5.core.interfaces import IProtectedContent
from plone.app.multilingual.interfaces import ITranslationManager



class GenwebControlPanelSettingsForm(controlpanel.RegistryEditForm):
    """ Genweb settings form """

    schema = IGenwebControlPanelSettings
    id = "GenwebControlPanelSettingsForm"
    label = _(u"Genweb UPC settings")
    description = _(u"help_genweb_settings_editform",
                    default=u"Configuracio de Genweb UPC ...")

    def updateFields(self):
        super(GenwebControlPanelSettingsForm, self).updateFields()

    def updateWidgets(self):
        super(GenwebControlPanelSettingsForm, self).updateWidgets()

    def link_translations(self, items):
        """
            Links the translations with the declared items with the form:
            [(obj1, lang1), (obj2, lang2), ...] assuming that the first element
            is the 'canonical' (in PAM there is no such thing).
        """
        # Grab the first item object and get its canonical handler
        canonical = ITranslationManager(items[0][0])

        for obj, language in items:
            if not canonical.has_translation(language):
                canonical.register_translation(language, obj)

    def create_content(self, container, portal_type, id, **kwargs):
        if not getattr(container, id, False):
            obj = createContentInContainer(container, portal_type, checkConstraints=False, **kwargs)
            self.publish_content(obj)
        return getattr(container, id)

    def publish_content(self, context):
        """ Make the content visible either in both possible genweb.simple and
            genweb.review workflows.
        """
        pw = getToolByName(context, "portal_workflow")
        object_workflow = pw.getWorkflowsFor(context)[0].id
        object_status = pw.getStatusOf(object_workflow, context)
        if object_status:
            api.content.transition(obj=context, transition={'genweb_simple': 'publish', 'genweb_review': 'publicaalaintranet'}[object_workflow])

    @button.buttonAndHandler(_('Save'), name=None)
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        create_packet = False
        if data.get('create_packet'):
            create_packet = True
            data['create_packet'] = False

        self.applyChanges(data)

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"), "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(),
                                                  self.control_panel_view))


class GenwebControlPanel(controlpanel.ControlPanelFormWrapper):
    """ Genweb settings control panel """
    form = GenwebControlPanelSettingsForm
    # index = ViewPageTemplateFile('controlpanel.pt')
