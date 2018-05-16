# -*- coding: utf-8 -*-
from zope import schema
from plone.supermodel import model

from base5.core import _

from plone.directives import form
from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield.registry import DictRow


class ITableEmailContact(form.Schema):
    language = schema.Choice(
        title=_(u'Language'),
        vocabulary=u'plone.app.vocabularies.SupportedContentLanguages',
        required=False
        )
    name = schema.TextLine(title=_(u'Name'),
                           required=False)
    email = schema.TextLine(title=_(u'E-mail'),
                            required=False)


class IGenwebControlPanelSettings(model.Schema):
    """ Global Genweb settings. This describes records stored in the
    configuration registry and obtainable via plone.registry.
    """

    model.fieldset('General',
                   _(u'General'),
                   fields=['html_title_ca', 'html_title_es', 'html_title_en',
                           'signatura_unitat_ca', 'signatura_unitat_es', 'signatura_unitat_en',
                           'right_logo_enabled', 'right_logo_alt', 'meta_author'])

    model.fieldset('Contact information',
                   _(u'Contact information'),
                   fields=['contacte_id', 'contacte_BBDD_or_page', 'contacte_al_peu',
                           'directori_upc', 'directori_filtrat', 'contacte_no_upcmaps', 'contacte_multi_email'
                           ])

    model.fieldset('Specific',
                   _(u'Specific'),
                   fields=['especific1', 'especific2',
                           'treu_imatge_capsalera', 'treu_menu_horitzontal',
                           'treu_icones_xarxes_socials', 'amaga_identificacio',
                           'idiomes_publicats',
                           'languages_link_to_root'])

    model.fieldset('Master',
                   _(u'Master'),
                   fields=['idestudi_master', 'create_packet'])

    model.fieldset('Custom Link',
                   _(u'Custom Link'),
                   fields=['cl_title_ca', 'cl_url_ca', 'cl_img_ca', 'cl_open_new_window_ca', 'cl_enable_ca',
                           'cl_title_es', 'cl_url_es', 'cl_img_es', 'cl_open_new_window_es', 'cl_enable_es',
                           'cl_title_en', 'cl_url_en', 'cl_img_en', 'cl_open_new_window_en', 'cl_enable_en'])

    # General section

    html_title_ca = schema.TextLine(
        title=_(u"html_title_ca",
                default=u"Titol del web amb HTML tags (negretes) [CA]"),
        description=_(u"help_html_title_ca",
                      default=u"Afegiu el titol del Genweb. Podeu incloure tags HTML"),
        required=False,
        # default=False,
        )

    html_title_es = schema.TextLine(
        title=_(u"html_title_es",
                default=u"Titol del web amb HTML tags (negretes) [ES]"),
        description=_(u"help_html_title_es",
                      default=u"Afegiu el titol del Genweb. Podeu incloure tags HTML"),
        required=False,
        # default=False,
        )

    html_title_en = schema.TextLine(
        title=_(u"html_title_en",
                default=u"Titol del web amb HTML tags (negretes) [EN]"),
        description=_(u"help_html_title_en",
                      default=u"Afegiu el titol del Genweb. Podeu incloure tags HTML."),
        required=False,
        # default=False,
        )

    signatura_unitat_ca = schema.TextLine(
        title=_(u"signatura_unitat_ca",
                default=u"Signatura de la unitat [CA]"),
        description=_(u"help_signatura_unitat_ca",
                      default=u"Es el literal que apareix al peu de pagina o el text alternatiu del logotip (centres docents)."),
        required=False,
        # default=False,
        )

    signatura_unitat_es = schema.TextLine(
        title=_(u"signatura_unitat_es",
                default=u"Signatura de la unitat [ES]"),
        description=_(u"help_signatura_unitat_es",
                      default=u"Es el literal que apareix al peu de pagina o el text alternatiu del logotip (centres docents)."),
        required=False,
        # default=False,
        )

    signatura_unitat_en = schema.TextLine(
        title=_(u"signatura_unitat_en",
                default=u"Signatura de la unitat [EN]"),
        description=_(u"help_signatura_unitat_en",
                      default=u"Es el literal que apareix al peu de pagina o el text alternatiu del logotip (centres docents)."),
        required=False,
        # default=False,
        )

    right_logo_enabled = schema.Bool(
        title=_(u"right_logo_enabled",
                default=u"Mostrar logo dret"),
        description=_(u"help_right_logo_enabled",
                      default=u"Mostra o no el logo dret de la capcalera."),
        required=False,
        default=False,
        )

    right_logo_alt = schema.TextLine(
        title=_(u"right_logo_alt",
                default=u"Text alternatiu del logo dret"),
        description=_(u"help_right_logo_alt",
                      default=u"Afegiu el text alternatiu (alt) del logo dret de la capcalera."),
        required=False,
        )

    meta_author = schema.TextLine(
        title=_(u'Meta author tag content'),
        description=_(u'Contingut de la etiqueta meta \"author\"'),
        required=False,
        default=u'UPC. Universitat Politecnica de Catalunya'
        )

    # Contact Information section

    contacte_id = schema.TextLine(
        title=_(u"contacte_id",
                default=u"ID contacte de la unitat"),
        description=_(u"help_contacte_id",
                      default=u"Afegiu el id de contacte de la base de dades de masters."),
        required=False,
        # default=False,
        )

    contacte_BBDD_or_page = schema.Bool(
        title=_(u"contacte_BBBDD_or_page",
                default=u"Pagina de contacte personalitzada"),
        description=_(u"help_contacte_BBBDD_or_page",
                      default=u"Per defecte, la informacio de contacte prove de la base de dades de SCP, sota peticio."),
        required=False,
        default=False,
        )

    contacte_al_peu = schema.Bool(
        title=_(u"contacte_al_peu",
                default=u"Adreca de contacte al peu"),
        description=_(u"help_contacte_al_peu",
                      default=u"La informacio provinent de la base de dades de SCP es visualitzen al peu de la pagina."),
        required=False,
        default=False,
        )

    directori_upc = schema.Bool(
        title=_(u"directori_upc",
                default=u"Directori UPC a les eines"),
        description=_(u"help_directori_upc",
                      default=u"Es mostrara a la part superior l'enllac al Directori UPC."),
        required=False,
        default=False,
        )

    directori_filtrat = schema.Bool(
        title=_(u"directori_filtrat",
                default=u"Directori UPC filtrat a les eines"),
        description=_(u"help_directori_filtrat",
                      default=u"S'obrira el Directori UPC, carregant les dades de la unitat."),
        required=False,
        default=False,
        )

    contacte_no_upcmaps = schema.Bool(
        title=_(u"contacte_no_upcmaps",
                default=u"Contacte sense UPCmaps"),
        description=_(u"help_contacte_no_upcmaps",
                      default=u"Es mostra la informacio d'UPCmaps al contacte."),
        required=False,
        default=False,
        )

    contacte_multi_email = schema.Bool(
        title=_(u"multi_email",
                default=u"Seleccionar l'adreca d'enviament"),
        description=_(u"help_contacte_multi_email",
                      default=u"Es pot seleccionar a qui s'envia el missatge de contacte."),
        required=False,
        default=False,
        )

    # Specific section

    especific1 = schema.TextLine(
        title=_(u"especific1",
                default=u"Color especific 1"),
        description=_(u"help_especific1",
                      default=u"Afegiu el color especific 1. es aquell que..."),
        required=False,
        # default=False,
        )

    especific2 = schema.TextLine(
        title=_(u"especific2",
                default=u"Color especific 2"),
        description=_(u"help_especific2",
                      default=u"Afegiu el color especific 2. es aquell que..."),
        required=False,
        # default=False,
        )

    treu_imatge_capsalera = schema.Bool(
        title=_(u"treu_imatge_capsalera",
                default=u"Treu la imatge de la capcalera"),
        description=_(u"help_treu_imatge_capsalera",
                      default=u"Treiem la imatge de la capcalera per ..."),
        required=False,
        default=False,
        )

    treu_menu_horitzontal = schema.Bool(
        title=_(u"treu_menu_horitzontal",
                default="Treu el menu horitzontal"),
        description=_(u"help_treu_menu_horitzontal",
                      default=u"Treu el menu horitzontal ..."),
        required=False,
        default=False,
        )

    treu_icones_xarxes_socials = schema.Bool(
        title=_(u"treu_icones_xarxes_socials",
                default="Treu les icones per compartir en xarxes socials"),
        description=_(u"help_treu_icones_xarxes_socials",
                      default=u"Treu les icones per compartir en xarxes socials ..."),
        required=False,
        default=False,
        )

    amaga_identificacio = schema.Bool(
        title=_(u"amaga_identificacio",
                default="Amaga de les eines l'enllac d'identificacio"),
        description=_(u"help_amaga_identificacio",
                      default=u"Amaga de les eines l'enllac d'identificacio ..."),
        required=False,
        default=False,
        )

    idiomes_publicats = schema.List(
        title=_(u"idiomes_publicats",
                default=u"Idiomes publicats al web"),
        description=_(u"help_idiomes_publicats",
                      default=u"Aquests seran els idiomes publicats a la web, els idiomes no especificats no seran publics pero seran visibles pels gestors (editors)."),
        value_type=schema.Choice(vocabulary='plone.app.vocabularies.SupportedContentLanguages'),
        required=False,
        default=['ca']
        )

    languages_link_to_root = schema.Bool(
        title=_(u"languages_link_to_root",
                default=u"languages_link_to_root"),
        description=_(u"help_languages_link_to_root",
                      default=u"help_languages_link_to_root"),
        required=False,
        default=False,
        )

    # Master section

    idestudi_master = schema.TextLine(
        title=_(u"idestudi_master",
                default=u"id_estudi"),
        description=_(u"help_idestudi_master",
                      default=u"Afegiu el id de l'estudi de la base de dades de masters."),
        required=False,
        # default=False,
        )

    # Boolean that marks if a packet in the root folder should be created
    create_packet = schema.Bool(
        title=_(u"create_packet",
                default=u"Create packet UPC at root"),
        description=_(u"help_create_packet",
                      default=u"help_create_packet"),
        required=False,
        default=False,
        )

    # Custom Link

    cl_title_ca = schema.TextLine(
        title=_(u"cl_title_ca",
                default=u"Link title [CA]"),
        description=_(u"help_cl_title",
                      default=u"Literal de l'enllac que es mostrara al menu superior dret"),
        required=False,
        )

    cl_url_ca = schema.URI(
        title=_(u"url_cl",
                default=u"Enllac per al menu superior"),
        description=_(u"help_cl_url",
                      default=u"URL de l'enllac que es mostrara al menu superior dret"),
        required=False,
        )

    cl_img_ca = schema.URI(
        title=_(u"img_cl",
                default=u"Enllac per a la icona del menu superior"),
        description=_(u"help_cl_img",
                      default=u"URL de l'enllac a la imatge que es mostrara al menu superior dret"),
        required=False,
        )

    cl_open_new_window_ca = schema.Bool(
        title=_(u"cl_oinw",
                default=u"Obre en una nova finestra"),
        description=_(u"help_cl_oinw",
                      default=u"Selecciona per obrir en una nova finestra"),
        required=False,
        default=False,
        )

    cl_enable_ca = schema.Bool(
        title=_(u"cl_enable",
                default=u"Publica l'enllac customitzat"),
        description=_(u"help_cl_enable",
                      default=u"Selecciona per publicar l'enllac"),
        required=False,
        default=False,
        )

    cl_title_es = schema.TextLine(
        title=_(u"cl_title_es",
                default=u"Link title [ES]"),
        description=_(u"help_cl_title",
                      default=u"Literal de l'enllac que es mostrara al menu superior dret"),
        required=False,
        )

    cl_url_es = schema.URI(
        title=_(u"url_cl",
                default=u"Enllac per al menu superior"),
        description=_(u"help_cl_url",
                      default=u"URL de l'enllac que es mostrara al menu superior dret"),
        required=False,
        )

    cl_img_es = schema.URI(
        title=_(u"img_cl",
                default=u"Enllac per a la icona del menu superior"),
        description=_(u"help_cl_img",
                      default=u"URL de l'enllac a la imatge que es mostrara al menu superior dret"),
        required=False,
        )

    cl_open_new_window_es = schema.Bool(
        title=_(u"cl_oinw",
                default=u"Obre en una nova finestra"),
        description=_(u"help_cl_oinw",
                      default=u"Selecciona per obrir en una nova finestra"),
        required=False,
        default=False,
        )

    cl_enable_es = schema.Bool(
        title=_(u"cl_enable",
                default=u"Publica l'enllac customitzat"),
        description=_(u"help_cl_enable",
                      default=u"Selecciona per publicar l'enllac"),
        required=False,
        default=False,
        )

    cl_title_en = schema.TextLine(
        title=_(u"cl_title_en",
                default=u"Link title [EN]"),
        description=_(u"help_cl_title",
                      default=u"Literal de l'enllac que es mostrara al menu superior dret"),
        required=False,
        )

    cl_url_en = schema.URI(
        title=_(u"url_cl",
                default=u"Enllac per al menu superior"),
        description=_(u"help_cl_url",
                      default=u"URL de l'enllac que es mostrara al menu superior dret"),
        required=False,
        )

    cl_img_en = schema.URI(
        title=_(u"img_cl",
                default=u"Enllac per a la icona del menu superior"),
        description=_(u"help_cl_img",
                      default=u"URL de l'enllac a la imatge que es mostrara al menu superior dret"),
        required=False,
        )

    cl_open_new_window_en = schema.Bool(
        title=_(u"cl_oinw",
                default=u"Obre en una nova finestra"),
        description=_(u"help_cl_oinw",
                      default=u"Selecciona per obrir en una nova finestra"),
        required=False,
        default=False,
        )

    cl_enable_en = schema.Bool(
        title=_(u"cl_enable",
                default=u"Publica l'enllac customitzat"),
        description=_(u"help_cl_enable",
                      default=u"Selecciona per publicar l'enllac"),
        required=False,
        default=False,
        )
