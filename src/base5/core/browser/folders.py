import os
import transaction
from datetime import datetime
from plone import api
from plone.namedfile import NamedBlobFile
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage


class DownloadFiles(BrowserView):

    template = ViewPageTemplateFile('templates/download_files.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self):
        form = self.request.form
        if not form or 'file_type' not in form:
            return self.template()

        from_path = '/'.join(self.context.getPhysicalPath())
        files = api.content.find(
            path=from_path,
            portal_type='File',
        )
        images = api.content.find(
            path=from_path,
            portal_type='Image',
        )
        if not files and not images:
            IStatusMessage(self.request).addStatusMessage(u"No files found!", "info")
            return self.template()
        
        today = datetime.today().strftime("%Y-%m-%d")
        exp_path = 'export-{0}-{1}'.format(self.context.id, today)
        if os.path.exists(exp_path):
            os.system('rm -rf {}'.format(exp_path))
        os.mkdir(exp_path)
        for file in files:
            obj = file.getObject()
            if form.get('file_type') == 'pdf' and 'pdf' not in obj.file.contentType:
                continue
            filename = obj.file.filename
            f = open(os.path.join(exp_path, filename), 'wb')
            f.write(obj.file.data)
            f.close()
            print("Saved {}".format(filename))
        for image in images:
            obj = image.getObject()
            if form.get('file_type') == 'img':
                continue
            filename = obj.image.filename
            f = open(os.path.join(exp_path, filename), 'wb')
            f.write(obj.image.data)
            f.close()
            print("Saved {}".format(filename))
        os.system('zip -r {0}.zip {0}'.format(exp_path))
        os.system('rm -rf {}'.format(exp_path))
        zip_file = api.content.create(
            type='File',
            title=exp_path,
            container=self.context,
        )
        zip_file.file = NamedBlobFile(
            data=open('{}.zip'.format(exp_path), 'r'),
            filename=u'{}.zip'.format(exp_path),
            contentType='application/zip'
        )
        zip_file.reindexObject()
        transaction.commit()
        self.request.response.redirect(zip_file.absolute_url() + '/view')