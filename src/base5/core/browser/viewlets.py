from five import grok
from plone import api
from zope.interface import Interface
from plone.memoize import forever
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import json
import pkg_resources


class gwCSSViewletManager(grok.ViewletManager):
    grok.context(Interface)
    grok.name('genweb.css')


class gwJSViewletManager(grok.ViewletManager):
    grok.context(Interface)
    grok.name('genweb.js')


class baseResourcesViewlet(grok.Viewlet):
    """ This is the base CSS and JS viewlet. """
    grok.baseclass()

    resource_type = None
    current_egg_name = None

    index_css = ViewPageTemplateFile('viewlets_templates/gwcssviewlet.pt')
    index_js = ViewPageTemplateFile('viewlets_templates/gwjsviewlet.pt')

    def render(self):
        if self.resource_type == 'css':
            return self.index_css()
        if self.resource_type == 'js':
            return self.index_js()

    def is_devel_mode(self):
        return api.env.debug_mode()

    def read_resource_config_file(self):
        egg = pkg_resources.get_distribution(self.current_egg_name)
        config_path = '{}/{}/config.json'.format(egg.location, self.current_egg_name.replace('.', '/'))
        resource_file = open(config_path)
        return resource_file.read()

    def get_resources(self):
        if self.is_devel_mode():
            return self.get_development_resources()
        else:
            return self.get_production_resources()

    @forever.memoize
    def get_development_resources(self):
        true_http_path = []
        resources_conf = json.loads(self.read_resource_config_file())
        replace_map = resources_conf['replace_map']

        for kind in resources_conf['order']:
            devel_resources = resources_conf['resources'][kind][self.resource_type]['development']
            for resource in devel_resources:
                found = False
                for source, destination in replace_map.items():
                    if source in resource:
                        true_http_path.append(resource.replace(source, destination))
                        found = True
                if not found:
                    true_http_path.append(resource)

        return true_http_path

    @forever.memoize
    def get_production_resources(self):
        true_http_path = []
        resources_conf = json.loads(self.read_resource_config_file())
        replace_map = resources_conf['replace_map']
        for kind in resources_conf['order']:
            production_resources = resources_conf['resources'][kind][self.resource_type]['production']
            for resource in production_resources:
                for res_rev_key in resources_conf['revision_info']:
                    if resource == res_rev_key:
                        resource = resources_conf['revision_info'][res_rev_key]

                found = False
                for source, destination in replace_map.items():
                    if source in resource:
                        true_http_path.append(resource.replace(source, destination))
                        found = True
                if not found:
                    true_http_path.append(resource)

        return true_http_path
