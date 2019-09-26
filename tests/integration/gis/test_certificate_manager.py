#-------------------------------------------------------------------------------
# Name:        CertificateManager class tests
# Purpose:     Sanity tests for ArcGIS Python API
#-------------------------------------------------------------------------------
import sys
import unittest
import pytest

from arcgis.gis import GIS
profiles = ['your_online_profile']
for profile in profiles:
    gis = GIS(profile=profile, verify_cert=False)
    assert gis.admin.certificates
    cm = gis.admin.certificates
    assert cm.properties
    assert isinstance(gis.admin.certificates.certificates, (list, tuple))
    with open(r"./cert_test.txt", 'r') as reader:
        result = cm.add(name='MYSELFSIGNEDCERT', domain='esri.com', certificate=reader.read())
        assert result
        for c in [cert['id'] for cert in cm.certificates if cert['name'] == 'MYSELFSIGNEDCERT']:
            g = cm.get(c)
            assert g
            assert g['name'] == "MYSELFSIGNEDCERT"
            assert cm.update(c, name='foodbar')
            g = cm.get(c)
            assert g
            assert g['name'] == "foodbar"
            assert cm.delete(c)
    [cm.delete(c['id']) for c in cm.certificates if c['name'] in ['foodbar', 'MYSELFSIGNEDCERT']] # CLEAN UP SCRIPT
