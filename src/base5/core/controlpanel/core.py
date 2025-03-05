# -*- coding: utf-8 -*-
from base5.core import _
from base5.core.utilities import IElasticSearch
from plone.app.registry.browser import controlpanel
from plone.supermodel import model
from Products.statusmessages.interfaces import IStatusMessage
from souper.interfaces import ICatalogFactory
from z3c.form import button
from zope import schema
from zope.component import getUtilitiesFor, getUtility
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary


class RegisteredExtendersVocabulary(object):

    def __call__(self, context):
        terms = []
        extenders = [a[0] for a in getUtilitiesFor(ICatalogFactory) if a[0].startswith('user_properties') and a[0] != 'user_properties']
        for extender in extenders:
            terms.append(SimpleVocabulary.createTerm(extender, str(extender), extender))
        return SimpleVocabulary(terms)

RegisteredExtendersVocabularyFactory = RegisteredExtendersVocabulary()


class IBaseCoreControlPanelSettings(Interface):
    """ Global Base settings. This describes records stored in the
    configuration registry and obtainable via plone.registry.
    """

    model.fieldset('General',
                   ('General'),
                   fields=['user_properties_extender',
                           'custom_editor_icons',
                           'elasticsearch'])

    model.fieldset('Ldap',
                   ('Ldap'),
                   fields=['alt_ldap_uri',
                           'alt_bind_dn',
                           'alt_bindpasswd',
                           'alt_base_dn',
                           'groups_query',
                           'user_groups_query',
                           'create_group_type'])

    user_properties_extender = schema.TextLine(
        title=_('User properties extender'),
        required=False,
        default=''
    )

    custom_editor_icons = schema.List(
        title=_('Llista personalitzada d\'icones per l\'editor TinyMCE'),
        description=_('Cada línia és una fila d\'icones. Si es deixa en blanc s\'agafen els valors per defecte. Han d\'omplir-se fins a 4 files obligatòriament.'),
        value_type=schema.TextLine(),
        required=False,
        default=[]
    )

    elasticsearch = schema.TextLine(
        title=_("elasticsearch",
                default="ElasticSearch"),
        description=_("elasticsearch_help",
                      default="URL del servidor d'ElasticSearch per aquest site"),
        required=False,
        default='localhost',
    )

    alt_ldap_uri = schema.TextLine(
        title=_("alt_ldap_uri",
                default="alt_ldap_uri"),
        description=_("alt_ldap_uri_help",
                      default="URL del servidor ldap per aquest site"),
        required=False,
        default='',
    )

    alt_bind_dn = schema.TextLine(
        title=_("alt_bind_dn",
                default="alt_bind_dn"),
        description=_("alt_bind_dn_help",
                      default="LDAP bind dn"),
        required=False,
        default='',
    )

    alt_bindpasswd = schema.TextLine(
        title=_("alt_bindpasswd",
                default="alt_bindpasswd"),
        description=_("alt_bindpasswd_help",
                      default="LDAP bind password"),
        required=False,
        default='',
    )

    alt_base_dn = schema.TextLine(
        title=_("alt_base_dn",
                default="alt_base_dn"),
        description=_("alt_base_dn_help",
                      default="LDAP base dn"),
        required=False,
        default='',
    )

    groups_query = schema.TextLine(
        title=_("groups_query",
                default="groups_query"),
        description=_("groups_query_help",
                      default="LDAP groups query. Ex: (&(objectClass=groupOfNames))"),
        required=False,
        default='',
    )

    user_groups_query = schema.TextLine(
        title=_("user_groups_query",
                default="user_groups_query"),
        description=_("user_groups_query_help",
                      default="LDAP user groups query. Ex: (&(objectClass=groupOfNames)(member=%s))"),
        required=False,
        default='',
    )

    create_group_type = schema.TextLine(
        title=_("create_group_type",
                default="create_group_type"),
        description=_("Type of group to create on ldap",
                      default="groupOfNames or groupOfUniqueNames"),
        required=False,
        default='groupOfNames',
    )


class BaseCoreControlPanelSettingsForm(controlpanel.RegistryEditForm):
    """ Base settings form """

    schema = IBaseCoreControlPanelSettings
    id = "BaseCoreControlPanelSettingsForm"
    label = _("Base settings")
    description = _("help_base_core_settings_editform",
                    default="Configuracio de Base Core")

    def updateFields(self):
        super(BaseCoreControlPanelSettingsForm, self).updateFields()

    def updateWidgets(self):
        super(BaseCoreControlPanelSettingsForm, self).updateWidgets()

    @button.buttonAndHandler(_('Save'), name=None)
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.applyChanges(data)

        es = getUtility(IElasticSearch)
        es.create_new_connection()

        IStatusMessage(self.request).addStatusMessage(_("Changes saved"), "info")
        self.context.REQUEST.RESPONSE.redirect("@@base-controlpanel")

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Edit cancelled"), "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(),
                                                  self.control_panel_view))


class BaseCoreControlPanel(controlpanel.ControlPanelFormWrapper):
    """ Base settings control panel """
    form = BaseCoreControlPanelSettingsForm
