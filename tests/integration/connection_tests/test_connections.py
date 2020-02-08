import sys
sys.path.insert(0, r"C:\SVN\achapkowski_geosaurus_fork_requests_take2\src")

import json
import pytest
import unittest
from arcgis.gis._impl._con import Connection


config_file = './connection.json'


class TestAGOLConnections(unittest.TestCase):
    """
    ArcGIS Online Connection Tests
    """
    def setUp(self):
        
        self._username_agol = None
        self._password_agol = None        
        self._client_id_agol = None
        self._client_secret_agol = None
        self._url_portal = None
        self._username_portal = None
        self._password_portal = None        
        self._client_id_portal = None
        self._client_secret_portal = None        
        with open(config_file, 'r') as reader:
            config = json.loads(reader.read())
            self._username_agol = config['username_agol']#
            self._password_agol = config['password_agol'] #           
            self._client_id_agol = config['client_id_agol']
            self._client_secret_agol = config['client_secret_agol']            
            
            self._url_portal = config['url_portal']
            self._username_portal = config['username_portal']
            self._password_portal = config['password_portal']
            self._client_id_portal = config['client_id_portal']
            self._client_secret_portal = config['client_secret_portal']                    
    #----------------------------------------------------------------------
    #@unittest.skip(reason='passed')
    def test_anonymous_agol(self):
        con = Connection()
        resp_get = con.get("portals/self", {'f' : "json"})
        assert resp_get
        resp_post = con.post("portals/self", {'f' : "json"})
        assert resp_post
    #----------------------------------------------------------------------
    #@unittest.skip(reason='passed')
    def test_built_in_agol(self):
        con = Connection(username=self._username_agol, password=self._password_agol, verify_cert=False)
        assert con.token
        resp_get = con.get("portals/self", {'f' : "json"})
        assert resp_get
        assert 'user' in resp_get
        resp_post = con.post("portals/self", {'f' : "json"})
        assert resp_post
        assert 'user' in resp_post
    #----------------------------------------------------------------------
    #@unittest.skip(reason='skip')
    def test_oauth_client_and_secret(self):
        """
        oauth with client and secret given
        
        
        **Setting up this test**
        
        - Create an app
        - add ```urn:ietf:wg:oauth:2.0:oob``` to redirect 
        - copy the client id and client_secret to the script
        
        
        """
        con = Connection(client_id=self._client_id_agol, 
                         client_secret=self._client_secret_agol, 
                         verify_cert=False)
        res = con.get("portals/self", {'f' : 'json'})
        assert 'appInfo' in res
        assert res['appInfo']['appOwner']
        res = con.post("portals/self", {'f' : 'json'})
        assert 'appInfo' in res
        assert res['appInfo']['appOwner']        
    #----------------------------------------------------------------------
    #@unittest.skip(reason='skip')
    def test_oauth_with_username(self):
        """
        oauth with client, username and password
        
        **Setting up this test**
        
        - Create an app
        - add ```urn:ietf:wg:oauth:2.0:oob``` to redirect 
        - copy the client id
        - provide a username/password
        
        
        """
        con = Connection(client_id=self._client_id_agol, 
                         username=self._username_agol, 
                         password=self._password_agol, 
                         verify_cert=False)
        res = con.get("portals/self", {'f' : 'json'})
        assert 'appInfo' in res
        assert 'user' in res
        
        res = con.post("portals/self", {'f' : 'json'})
        assert 'appInfo' in res
        assert 'user' in res        
    #----------------------------------------------------------------------
    @unittest.skip(reason='requires human interaction.')
    def test_oauth_no_username(self):
        """
        oauth with client ONLY
        
        **Setting up this test**
        
        - Create an app
        - add ```urn:ietf:wg:oauth:2.0:oob``` to redirect 
        - copy the client id into script
        - manually follow instructions.
        
        """        
        con = Connection(client_id=self._client_id_agol,
                         verify_cert=False)
        
        res = con.get("portals/self", {'f' : 'json'})
        assert 'appInfo' in res
        assert 'user' in res
        
        res = con.post("portals/self", {'f' : 'json'})
        assert 'appInfo' in res
        assert 'user' in res                
    
###########################################################################
class TestPortalConnection(unittest.TestCase):
    """
    Portal Connection Tests
    """    
    def setUp(self):
        
        self._username_agol = None
        self._password_agol = None        
        self._client_id_agol = None
        self._client_secret_agol = None
        self._url_portal = None
        self._username_portal = None
        self._password_portal = None        
        self._client_id_portal = None
        self._client_secret_portal = None        
        self._portal_iwa = None
        self._duel_iwa = None        
        self._kerberos_portal = None
        self._portal_tier = None
        self._portal_xldapds = None
        
        with open(config_file, 'r') as reader:
            config = json.loads(reader.read())
            self._username_agol = config['username_agol']#
            self._password_agol = config['password_agol'] #           
            self._client_id_agol = config['client_id_agol']
            self._client_secret_agol = config['client_secret_agol']            
            
            self._url_portal = config['url_portal']
            self._username_portal = config['username_portal']
            self._password_portal = config['password_portal']
            self._client_id_portal = config['client_id_portal']
            self._client_secret_portal = config['client_secret_portal']   
            self._portal_iwa = config["iwa_portal"]
            self._duel_iwa = config["duel_iwa"]
            self._kerberos_portal = config["kerberos"]
            self._portal_tier = config["portal_tier"]
            self._portal_xldapds = config["portal_xldapds"]
    #----------------------------------------------------------------------
    #@unittest.skip(reason='skip')
    def test_iwa(self):
        """iwa test"""
        for iwa_url in [self._portal_iwa, self._duel_iwa]:
            con = Connection(iwa_url, verify_cert=False)
            resp_get = con.get("portals/self", {'f' : "json"})
            assert resp_get
            assert 'user' in resp_get
            resp_post = con.post("portals/self", {'f' : "json"})
            assert resp_post
            assert 'user' in resp_post
    #----------------------------------------------------------------------
    #@unittest.skip(reason='skip')
    def test_kerberos(self):
        """test kerberos security"""
        for url in [self._kerberos_portal ]:
            con = Connection(url, verify_cert=False)
            resp_get = con.get("portals/self", {'f' : "json"})
            assert resp_get
            assert 'user' in resp_get
            resp_post = con.post("portals/self", {'f' : "json"})
            assert resp_post
            assert 'user' in resp_post
    #----------------------------------------------------------------------
    #@unittest.skip(reason='passed')
    def test_anonymous_portal(self):
        con = Connection(baseurl=self._url_portal)
        resp_get = con.get("portals/self", {'f' : "json"})
        assert resp_get
        resp_post = con.post("portals/self", {'f' : "json"})
        assert resp_post
    #----------------------------------------------------------------------
    #@unittest.skip(reason='passed')
    def test_built_in_portal(self):
        con = Connection(baseurl=self._url_portal, 
                         username=self._username_portal, 
                         password=self._password_portal)
        assert con.token
        resp_get = con.get("portals/self", {'f' : "json"})
        assert resp_get
        assert 'user' in resp_get
        resp_post = con.post("portals/self", {'f' : "json"})
        assert resp_post
        assert 'user' in resp_post
    #----------------------------------------------------------------------
    #@unittest.skip(reason='skip')
    def test_oauth_client_and_secret(self):
        """
        oauth with client and secret given
        
        
        **Setting up this test**
        
        - Create an app
        - add ```urn:ietf:wg:oauth:2.0:oob``` to redirect 
        - copy the client id and client_secret to the script
        
        
        """
        con = Connection(self._url_portal,
                         client_id=self._client_id_portal, 
                         client_secret=self._client_secret_portal,
                         verify_cert=False)
        res = con.get("portals/self", {'f' : 'json'})
        assert 'appInfo' in res
        assert res['appInfo']['appOwner']
        res = con.post("portals/self", {'f' : 'json'})
        assert 'appInfo' in res
        assert res['appInfo']['appOwner']        
    #----------------------------------------------------------------------
    #@unittest.skip(reason='skip')
    def test_oauth_with_username(self):
        """
        oauth with client, username and password
        
        **Setting up this test**
        
        - Create an app
        - add ```urn:ietf:wg:oauth:2.0:oob``` to redirect 
        - copy the client id
        - provide a username/password
        
        
        """
        con = Connection(self._url_portal,
                         client_id=self._client_id_portal, 
                         username=self._username_portal, 
                         password=self._password_portal, 
                         verify_cert=False)
        res = con.get("portals/self", {'f' : 'json'})
        assert 'appInfo' in res
        assert 'user' in res
        
        res = con.post("portals/self", {'f' : 'json'})
        assert 'appInfo' in res
        assert 'user' in res        
    #----------------------------------------------------------------------
    @unittest.skip(reason='requires human interaction.')
    def test_oauth_no_username(self):
        """
        oauth with client ONLY
        
        **Setting up this test**
        
        - Create an app
        - add ```urn:ietf:wg:oauth:2.0:oob``` to redirect 
        - copy the client id into script
        - manually follow instructions.
        
        """        
        con = Connection(client_id=self._client_id_portal,
                         verify_cert=False)
        
        res = con.get("portals/self", {'f' : 'json'})
        assert 'appInfo' in res
        assert 'user' in res
        
        res = con.post("portals/self", {'f' : 'json'})
        assert 'appInfo' in res
        assert 'user' in res                    
        
    
        
if __name__ == '__main__':
    unittest.main()
