# -*- coding: utf-8 -*-
"""Installer for the base5.core package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='base5.core',
    version='0.55',
    description="Base Genweb, Ulearn, etc Plone 5",
    long_description=long_description,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone',
    author='Plone Team',
    author_email='plone.team@upcnet.es',
    url='https://pypi.python.org/pypi/base5.core',
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['base5'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'plone.api',
        'Products.GenericSetup>=1.8.2',
        'setuptools',
        'z3c.jbot',
        'pyquery',
        'elasticsearch',
        'souper.plone',
        'plone.tiles',
        'plone.subrequest',
        'plone.app.tiles',
        'plone.app.standardtiles',
        'plone.app.blocks',
        'plone.app.drafts',
        'plone.app.mosaic',
        'collective.dexteritytextindexer',
        'Products.PloneLDAP',
        'collective.z3cform.datagridfield',
        'BeautifulSoup',
        'pdfkit',
        'ulearn5.core'
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            'plone.testing>=5.0.0',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
            'unittest2',
            'ulearn5.core',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
