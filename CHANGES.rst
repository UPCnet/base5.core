Changelog
=========


0.48 (2021-03-25)
-----------------

* Index is_flash and is_outoflist only INewsItem not IDexterityContent [Pilar Marinas]
* Optimizar codigo portlet media [Pilar Marinas]
* Comentamos el modificar la imagen en el login porque da conflict error en el ZEO [Pilar Marinas]

0.47 (2021-03-08)
-----------------

* Si osiris devuelve BadUsernameOrPasswordError no continua mirando plugins autenticacion [Pilar Marinas]
* Que el LDAP no haga consulta dos veces si la primera vez el usuario devuelve Invalid credentials [Pilar Marinas]

0.46 (2021-02-05)
-----------------

* Quitar hora inicio en eventos de todo el dia [Pilar Marinas]

0.45 (2021-01-27)
-----------------

* Add path in view future events [Pilar Marinas]

0.44 (2021-01-27)
-----------------

* View future events [Pilar Marinas]

0.43 (2020-11-26)
-----------------

* Reemplazar getToolByName por api.portal.get_tool [Iago López Fernández]

0.42 (2020-11-18)
-----------------

* Merge remote-tracking branch 'origin/notificaciones' into develop [pilar.marinas]

0.41 (2020-11-16)
-----------------

* Vistas para ver y borrar usuarios que estan en el MAX pero no en el LDAP [Pilar Marinas]

0.40 (2020-11-11)
-----------------

* Quitar actualizar foto en login para medichem se hace en el rebuild_user_catalog [Pilar Marinas]
* Solucionar error UpdateUserPropertiesOnLogin [Pilar Marinas]
* Setup tinymce añadir atributos validos [Iago López Fernández]
* Imports que faltan [Pilar Marinas]

0.39 (2020-10-13)
-----------------

* Que el campo mail no se mire para el badget de la foto [Pilar Marinas]
* Modificar codigo para el badget de la imagen lo mire del soup y no actualize siempre foto [Pilar Marinas]

0.38 (2020-09-29)
-----------------

* Rendimiento: Portlet Media -> reducir la imagen a mini [Iago López Fernández]

0.37 (2020-09-17)
-----------------

* Parches para solucionar los usuarios con acento en el CN - DN de MEDICHEM [root]

0.36 (2020-09-08)
-----------------

* Quitar que se actulicen los datos de cornestone en el primer login medichem [Pilar Marinas]

0.35 (2020-07-23)
-----------------

* Modificar permiso WebMaster pueda cambiar vista carpeta y restricciones tipo contenido carpeta [Pilar Marinas]

0.34 (2020-07-20)
-----------------

* No actualizar datos usuario Medichem en login [Pilar Marinas]

0.33 (2020-06-09)
-----------------

* Quitar u daba error [root]
* API Cornestone perfil usuario [Pilar Marinas]
* get_events [Iago López Fernández]

0.32 (2020-04-28)
-----------------

* Solucionar si evento es de todo el dia o sin hora fin [Pilar Marinas]

0.31 (2020-04-27)
-----------------

* Modify format time events for user [Pilar Marinas]

0.30 (2020-03-20)
-----------------

* Arreglar error timezone pytz [Iago López Fernández]
* Ver evento con la timezone del usuario [Iago López Fernández]

0.29 (2020-03-03)
-----------------

* Add info logger [pilar.marinas]
* Log delete_user_catalog [Iago López Fernández]

0.28 (2020-02-19)
-----------------

* Guardar datos en el soup enginyersbcn al guardar datos usuario desde usuarios y grupos [pilar.marinas]

0.27 (2020-02-11)
-----------------

* Turn off email notifications entirely [pilar.marinas]
* Traducción grid_events_view [Iago López Fernández]
* Quitar notificacion travis [pilar.marinas]

0.26 (2020-01-14)
-----------------

* Añadir año a la vista de los eventos [Iago López Fernández]

0.25 (2019-12-18)
-----------------

* grid_events_view: Visualizar por fecha de inicio descendente [Iago López Fernández]

0.24 (2019-12-12)
-----------------

* Cambiar orden en la que se ven los eventos en la vista grid_events_view [Iago López Fernández]
* Setup tiny -> forced_root_block: p [Iago López Fernández]

0.23 (2019-11-06)
-----------------

* Sobreescribir template de los enlace para añadir blink [Iago López Fernández]

0.22 (2019-07-22)
-----------------

* Ldap group creation parametre [Vicente Iranzo Maestre]

0.21 (2019-06-26)
-----------------

* Traducciones ca collective.polls [Iago López Fernández]
* Traducción CA collective.easyform.po [Iago López Fernández]
* Travis [Pilar Marinas]
* Add package to test [Pilar Marinas]
* travis [Pilar Marinas]
* Travis [Pilar Marinas]

0.20 (2019-05-02)
-----------------

* Modify literals clouseau [Pilar Marinas]
* Soup i vistes delete_local_roles [Pilar Marinas]
* Traducción CA collective.easyform.po [Iago López Fernández]
* require ulearn5.core [Pilar Marinas]
* Solucionar test [Pilar Marinas]

0.19 (2019-04-15)
-----------------

* Que al guardar el profile se borren y se anadan todos los campos en el view_user_catalog [root]

0.18 (2019-04-01)
-----------------

* Solucionar guardar extender_properties in soup ASPB to rebuild_user_catalog [Pilar Marinas]
* Añadir list y tuplas en get_all_user_properties() [Iago López Fernández]
* Normalizar valores del widget select multiple en el searchable_text [Iago López Fernández]

0.17 (2019-03-18)
-----------------

* Revision permisos webmaster [Pilar Marinas]
* bypass tests version conflict [Roberto Diaz]

0.16 (2019-02-12)
-----------------

* Que no haya un batch huerfano [Pilar Marinas]
* Arreglar codificacion abrevia [Pilar Marinas]

0.15 (2019-02-11)
-----------------

* Añadir col-lg en la vista grid_events [Iago López Fernández]
* print to logger.info [Iago López Fernández]
* Clouseau: Formato documentación [Iago López Fernández]
* Traducciones [Iago López Fernández]
* Traducciones [Iago López Fernández]
* Fix browser/views_templates/macros.pt [Iago López Fernández]
* Refinar estils back vista esdeveniments [alberto.duran]
* Estils vista esdeveniments [alberto.duran]
* Añadir BeautifulSoup en install_requires [Iago López Fernández]
* Add abrevia with beautifulsoup [alberto.duran]
* Vista esdeveniments funcional, sense maquetar [alberto.duran]
* Quitar activación del plugin fullpage de TinyMCE en la vista setuptinymce [Iago López Fernández]

0.14 (2019-01-31)
-----------------

* Cron Task [Pilar Marinas]

0.13 (2018-12-18)
-----------------

* Solucionar parche para que no de error la creacion de usuarios [Pilar Marinas]

0.12 (2018-12-11)
-----------------

* add_user_to_catalog permitir listas [Iago López Fernández]

0.11 (2018-12-04)
-----------------

* memoize results portlet media [Pilar Marinas]
* Quitar plone_log [Pilar Marinas]
* Logger error rebuild_user_catalog [Pilar Marinas]
* setuptinymce: Cambiar configuración [Iago López Fernández]
* visible_userprofile_portlet por defecto a True [Iago López Fernández]

0.10 (2018-11-16)
-----------------

* Si hay ñ en el dn al hacer rebuild_user_catalog se lo salta y no da error [Pilar Marinas]

0.9 (2018-11-12)
----------------

* Vistas add/remove_user_catalog permitir multiples usuarios en la petición [Iago López Fernández]

0.8 (2018-11-08)
----------------

* removed code analysis [Roberto Diaz]
* Merge remote-tracking branch 'origin/master' into develop [Pilar Marinas]

0.7 (2018-10-30)
----------------

* Connection elestic url not equal localhost [Pilar Marinas]
* Si no hay url y check no hacer el elastic [Pilar Marinas]
* Añadir catalogo user_news_searches [iago.lopez]
* Solucionar test [Pilar Marinas]
* updated package to run travis. TODO: need solve missing phone in some tests [Roberto Diaz]

0.6 (2018-10-29)
----------------

* Modify UserPropertiesSoupCatalogFactory base with properties plone [Pilar Marinas]
* Quitar Genweb [Pilar Marinas]
* Add helpers add_user_catalog and remove_user_catalog: Add and remove a specific user in catalog [iago.lopez]

0.5 (2018-10-10)
----------------

* Merge externs [Pilar Marinas]
* Visibilidad campos del perfil: externs [iago.lopez]
* Visibilidad campos perfil por el usuario [iago.lopez]
* Visibilidad campos del perfil [iago.lopez]
* Solucion errores con usuario anonimo [iago.lopez]
* Quitar fuzzy [iago.lopez]
* Portlet Smart [iago.lopez]
* Portlet Smart [iago.lopez]

0.4 (2018-07-03)
----------------

* traduccions [root@comunitatsdevel]
* Traducciones [iago.lopez]
* Update parameter [root@comunitatsdevel]
* Update plugins for setupldapupc [alberto.duran]
* Update ldap configs [alberto.duran]
* Disable CSRF in delete_user_catalog [Pilar Marinas]
* Update view for tinymce configurator [alberto.duran]

0.3 (2018-06-07)
----------------

* SOLVED: Angular loaded 2 times in production mode, disabled [Roberto Diaz]
* Add coding [alberto.duran]

0.2 (2018-05-31)
----------------

* Delete user catalog [Pilar Marinas]
* Vista setupldapexterns: Enlazar al controlpanel correcto [iago.lopez]

0.1 (2018-05-22)
----------------

- Initial release.
  [pilar.marinas@upcnet.es]
