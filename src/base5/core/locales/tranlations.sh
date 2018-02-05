#!/bin/bash

domain=base

msgfmt -o ca/LC_MESSAGES/$domain.mo  ca/LC_MESSAGES/$domain.po
msgfmt -o es/LC_MESSAGES/$domain.mo  es/LC_MESSAGES/$domain.po
msgfmt -o en/LC_MESSAGES/$domain.mo  en/LC_MESSAGES/$domain.po


domainPortlets=base5.portlets

msgfmt -o ca/LC_MESSAGES/$domainPortlets.mo  ca/LC_MESSAGES/$domainPortlets.po
msgfmt -o es/LC_MESSAGES/$domainPortlets.mo  es/LC_MESSAGES/$domainPortlets.po
msgfmt -o en/LC_MESSAGES/$domainPortlets.mo  en/LC_MESSAGES/$domainPortlets.po
