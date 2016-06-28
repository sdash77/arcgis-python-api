""" The portalpy module for working with the ArcGIS Online and Portal APIs."""
from __future__ import absolute_import
__version__ = '1.0'

import collections
import json
import logging
import mimetypes
import os
import re
import unicodedata
import cgi
from io import StringIO
from collections import OrderedDict

import uuid
import zlib
import six
from six.moves.urllib_parse import urlparse, urlunparse, parse_qsl
from six.moves.urllib_parse import quote, unquote, urlunsplit
from six.moves.urllib_parse import urlencode, urlsplit
from six.moves.urllib.error import HTTPError
from six.moves.urllib import request
from six.moves import http_cookiejar as cookiejar
from six.moves import http_client

_log = logging.getLogger(__name__)

class HTTPSClientAuthHandler(request.HTTPSHandler):
    def __init__(self, key, cert):
        request.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert
    def https_open(self, req):
        #Rather than pass in a reference to a connection class, we pass in
        # a reference to a function which, for all intents and purposes,
        # will behave as a constructor
        return self.do_open(self.getConnection, req)
    def getConnection(self, host, timeout=300):
        return  http_client.HTTPSConnection(host,
                                            key_file=self.key,
                                            cert_file=self.cert,
                                            timeout=timeout)

class _ArcGISConnection(object):
    """ A class users to manage connection to ArcGIS services (Portal and Server). """
    baseurl = None
    key_file = None
    cert_file = None
    all_ssl = None
    proxy_host = None
    proxy_port = None
    token = None
    ensure_ascii = None
    _referer = None
    _useragent = None
    _parsed_org_url = None
    _username = None
    _password = None
    _auth = None
    #----------------------------------------------------------------------
    def __init__(self, baseurl, username=None, password=None, key_file=None,
                 cert_file=None, expiration=60, all_ssl=False, referer=None,
                 proxy_host=None, proxy_port=None, ensure_ascii=True):
        """ The _ArcGISConnection constructor. Requires URL and optionally username/password. """

        self.baseurl = baseurl
        '''_normalize_url(baseurl)'''
        self.key_file = key_file
        self.cert_file = cert_file
        self.all_ssl = all_ssl
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.ensure_ascii = ensure_ascii
        self.token = None

        # Setup the referer and user agent
        if not referer:
            referer = urlparse(baseurl).netloc
        self._referer = referer
        self._useragent = 'geosaurus/' + __version__

        parsed_url = urlparse(self.baseurl)
        self._parsed_org_url = urlunparse((parsed_url[0], parsed_url[1], "", "", "", ""))

        self._username = username
        self._password = password

        if cert_file is not None and key_file is not None:
            self._auth = "PKI"
        elif username is not None and password is not None:
            self._auth = "BUILTIN" # or "BASICAUTH" (LDAP) or NTLM or Kerberos (login sets this up)
        else:
            self._auth = "ANON"

        # Login if credentials were provided
        if username and password:
            self.login(username, password, expiration)
        elif username or password:
            _log.warning('Both username and password required for login')
    #----------------------------------------------------------------------
    def generate_token(self, username, password, expiration=60):
        """ Generates and returns a new token, but doesn't re-login. """
        postdata = { 'username': username, 'password': password,
                     'client': 'referer', 'referer': self._referer,
                     'expiration': expiration, 'f': 'json' }
        if self.baseurl.endswith('/'):
            resp = self.post('generateToken', postdata, ssl=True)
        else:
            resp = self.post('/generateToken', postdata, ssl=True)
        if resp:
            return resp.get('token')
    #----------------------------------------------------------------------
    def _make_boundary(self):
        """ creates a boundary for multipart post (form post)"""
        if six.PY2:
            return '-===============%s==' % uuid.uuid4().get_hex()
        elif six.PY3:
            return '-===============%s==' % uuid.uuid4().hex
        else:
            from random import choice
            digits = "0123456789"
            letters = "abcdefghijklmnopqrstuvwxyz"
            return '-===============%s==' % ''.join(choice(letters + digits) \
                                                   for i in range(15))
    #----------------------------------------------------------------------
    def login(self, username, password, expiration=60):
        """ Logs into the portal using username/password. """
        try:
            newtoken = self.generate_token(username, password, expiration)
            if newtoken:
                self.token = newtoken
                self._username = username
                self._password = password
                self._expiration = expiration
                self._auth = "BUILTIN"
            return newtoken
        except HTTPError as err:
            if err.code == 401: # using basic authentication
                self._auth = "BASICAUTH"
            else:
                raise
    #----------------------------------------------------------------------
    def relogin(self, expiration=None):
        """ Re-authenticates with the portal using the same username/password. """
        if not expiration:
            expiration = self._expiration
        return self.login(self._username, self._password, expiration)
    #----------------------------------------------------------------------
    def logout(self):
        """ Logs out of the portal. """
        self.token = None
    #----------------------------------------------------------------------
    def is_logged_in(self):
        """ Returns true if logged into the portal. """
        return self.token is not None
    #----------------------------------------------------------------------
    def _mainType(self, resp):
        """ gets the main type from the response object"""
        if six.PY2:
            return resp.headers.maintype
        elif six.PY3:
            return resp.headers.get_content_maintype()
        else:
            return None
    #----------------------------------------------------------------------
    def _process_response(self, resp):
        """ processes the response object"""
        CHUNK = 4056
        maintype = self._mainType(resp)
        contentDisposition = resp.headers.get('content-disposition')
        contentType = resp.headers.get('content-type')
        contentLength = resp.headers.get('content-length')
        if maintype.lower() in ('image',
                                'application/x-zip-compressed') or \
           contentType == 'application/x-zip-compressed' or \
           (contentDisposition is not None and \
            contentDisposition.lower().find('attachment;') > -1):
            if contentLength is not None:
                max_length = int(contentLength)
                if max_length < CHUNK:
                    CHUNK = max_length
            raw = None
            for data in self._chunk(response=resp):
                if raw is None:
                    raw = data
                else:
                    raw += data
                del data
            return raw
        else:
            read = ""
            for data in self._chunk(response=resp, size=CHUNK):
                if six.PY3 == True:
                    if read == "":
                        read = data
                    else:
                        read += data
                else:
                    read += data

                del data
            if six.PY3:
                read = read.decode("utf-8").strip()
            try:
                return read.strip()
            except:
                return read
        return ""
    #----------------------------------------------------------------------
    def _chunk(self, response, size=4096):
        """
        downloads a web response in pieces to ensure there are no
        memory issues.
        """
        method = response.headers.get("content-encoding")
        if method == "gzip":
            d = zlib.decompressobj(16+zlib.MAX_WBITS)
            b = response.read(size)
            while b:
                data = d.decompress(b)
                yield data
                b = response.read(size)
                del data
        else:
            while True:
                chunk = response.read(size)
                if not chunk: break
                yield chunk
    #----------------------------------------------------------------------
    def get(self, path, ssl=False, compress=True, try_json=True, is_retry=False, use_ordered_dict=False):
        """ Returns result of an HTTP GET. Handles token timeout and all SSL mode."""
        url = path
        if (len(url) > 0 and url[0] == '/' ) == False and \
            self.baseurl.endswith('/') == False:
            url = "/{path}".format(path=url)
        if not path.startswith('http://') and \
           not path.startswith('https://'):
            url = self.baseurl + url
        if ssl or self.all_ssl:
            url = url.replace('http://', 'https://')

        # Add the token if logged in
        if self.is_logged_in():
            url = self._url_add_token(url, self.token)

        _log.debug('REQUEST (get): ' + url)

        try:
            # Send the request and read the response
            headers = [('Referer', self._referer),
                       ('User-Agent', self._useragent)]
            if compress:
                headers.append(('Accept-encoding', 'gzip'))

            handlers = self.get_handlers()
            opener = request.build_opener(*handlers)
            opener.addheaders = headers
            request.install_opener(opener)
            req = request.Request(url)
            resp = request.urlopen(req)
            resp_data = self._process_response(resp)

            # If we're not trying to parse to JSON, return response as is
            if not try_json:
                return resp_data

            try:
                if use_ordered_dict:
                    resp_json = json.loads(resp_data,
                                           object_pairs_hook=OrderedDict)
                else:
                    resp_json = json.loads(resp_data)

                # Convert to ascii if directed to do so
                if self.ensure_ascii and not use_ordered_dict:
                    resp_json = _unicode_to_ascii(resp_json)

                # Check for errors, and handle the case where the token timed
                # out during use (and simply needs to be re-generated)
                try:
                    if resp_json.get('error', None):
                        errorcode = resp_json['error']['code']
                        if errorcode == 498 and not is_retry:
                            _log.info('Token expired during get request, ' \
                                      + 'fetching a new token and retrying')
                            newtoken = self.relogin()
                            newpath = self._url_add_token(path, newtoken)
                            return self.get(newpath, ssl, compress, try_json, is_retry=True)
                        elif errorcode == 498:
                            raise RuntimeError('Invalid token')
                        self._handle_json_error(resp_json['error'])
                        return None
                except AttributeError:
                    # Top-level JSON object isnt a dict, so can't have an error
                    pass

                # If the JSON parsed correctly and there are no errors,
                # return the JSON
                return resp_json

            # If we couldnt parse the response to JSON, return it as is
            except ValueError:
                return resp

        # If we got an HTTPError when making the request check to see if it's
        # related to token timeout, in which case, regenerate a token
        except HTTPError as e:
            if e.code == 498 and not is_retry:
                _log.info('Token expired during get request, fetching a new ' \
                          + 'token and retrying')
                self.logout()
                newtoken = self.relogin()
                newpath = self._url_add_token(path, newtoken)
                return self.get(newpath, ssl, try_json, is_retry=True)
            elif e.code == 498:
                raise RuntimeError('Invalid token')
            else:
                raise e
    #----------------------------------------------------------------------
    def _ensure_dir(self, f):
        if not os.path.exists(f):
            os.makedirs(f)
    #----------------------------------------------------------------------
    def download_to_folder(self, path, dir_name, ssl=False, is_retry=False):
        """ Downloads file to specified directory. Handles token timeout and all SSL mode."""
        url = path
        if not path.startswith('http://') and not path.startswith('https://'):
            url = self.baseurl + path
        if ssl or self.all_ssl:
            url = url.replace('http://', 'https://')

        # Add the token if logged in
        if self.is_logged_in():
            url = self._url_add_token(url, self.token)

        _log.debug('REQUEST (get): ' + url)

        try:
            # Send the request and read the response
            headers = [('Referer', self._referer),
                       ('User-Agent', self._useragent)]

            handlers = self.get_handlers()
            opener = request.build_opener(*handlers)

            opener.addheaders = headers
            resp = opener.open(url)
            resp_data = resp.read()

            content_disp = resp.info().get('Content-Disposition')
            if content_disp:
                value, params = cgi.parse_header(content_disp)
                filename = params['filename']
            else:
                filename = "data.bin"

            self._ensure_dir(dir_name)
            filename = os.path.join(dir_name, filename)

            f = open(filename, 'wb+')
            f.write(resp_data)
            f.close()

            return filename

        # If we got an HTTPError when making the request check to see if it's
        # related to token timeout, in which case, regenerate a token
        except HTTPError as e:
            if e.code == 498 and not is_retry:
                _log.info('Token expired during get request, fetching a new ' \
                          + 'token and retrying')
                self.logout()
                newtoken = self.relogin()
                newpath = self._url_add_token(path, newtoken)
                return self.download_to_folder(newpath, dir_name, ssl, is_retry=True)
            elif e.code == 498:
                raise RuntimeError('Invalid token')
            else:
                raise e
    #----------------------------------------------------------------------
    def download(self, path, filepath, ssl=False, is_retry=False):
        """ Downloads result of an HTTP GET. Handles token timeout and all SSL mode."""
        url = path
        if not path.startswith('http://') and not path.startswith('https://'):
            url = self.baseurl + path
        if ssl or self.all_ssl:
            url = url.replace('http://', 'https://')

        # Add the token if logged in
        if self.is_logged_in():
            url = self._url_add_token(url, self.token)

        _log.debug('REQUEST (download): ' + url + ', to ' + filepath)

        # Send the request, and handle the case where the token has
        # timed out (relogin and try again)
        try:
            opener = _StrictURLopener()
            opener.addheaders = [('Referer', self._referer),
                                 ('User-Agent', self._useragent)]
            opener.retrieve(url, filepath)
        except HTTPError as e:
            if e.code == 498 and not is_retry:
                _log.info('Token expired during download request, fetching a ' \
                          + 'new token and retrying')
                self.logout()
                newtoken = self.relogin()
                newpath = self._url_add_token(path, newtoken)
                self.download(newpath, filepath, ssl, is_retry=True)
            elif e.code == 498:
                raise RuntimeError('Invalid token')
            else:
                raise e
    #----------------------------------------------------------------------
    def _url_add_token(self, url, token):

        # Parse the URL and query string
        urlparts = urlparse(url)
        qs_list = parse_qsl(urlparts.query)

        # Update the token query string parameter
        replaced_token = False
        new_qs_list = []
        for qs_param in qs_list:
            if qs_param[0] == 'token':
                qs_param = ('token', token)
                replaced_token = True
            new_qs_list.append(qs_param)
        if not replaced_token:
            new_qs_list.append(('token', token))

        # Rebuild the URL from parts and return it
        return urlunparse((urlparts.scheme, urlparts.netloc,
                           urlparts.path, urlparts.params,
                           urlencode(new_qs_list),
                           urlparts.fragment))
    #----------------------------------------------------------------------
    def get_handlers(self):
        handlers = []

        if self._auth == "BASICAUTH": # used by LDAP
            passman = request.HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None,
                                 self._parsed_org_url,
                                 self._username,
                                 self._password)
            handlers.append(request.HTTPBasicAuthHandler(passman))

        if self._auth == "PKI":
            handlers.append(HTTPSClientAuthHandler(self.key_file, self.cert_file))

        cj = cookiejar.CookieJar()
        handlers.append(request.HTTPCookieProcessor(cj))
        return handlers
    #----------------------------------------------------------------------
    def post(self, path, postdata=None, files=None, ssl=False, compress=True,
             is_retry=False, use_ordered_dict=False, add_token=True):
        """ Returns result of an HTTP POST. Supports Multipart requests."""
        path = quote(path, ':/')
        url = path
        if (len(url) > 0 and url[0] == '/' ) == False and \
            self.baseurl.endswith('/') == False:
            url = "/{path}".format(path=url)
        if not path.startswith('http://') and \
           not path.startswith('https://'):
            url = self.baseurl + url
        if ssl or self.all_ssl:
            url = url.replace('http://', 'https://')

        # Add the token if logged in
        if add_token:
            if self.is_logged_in():
                postdata['token'] = self.token

        if _log.isEnabledFor(logging.DEBUG):
            msg = 'REQUEST: ' + url + ', ' + str(postdata)
            if files:
                msg += ', files=' + str(files)
            _log.debug(msg)

        # If there are files present, send a multipart request
        if files:
            parsed_url = urlparse(url)
            resp_data = self._postmultipart(parsed_url.netloc,
                                            str(parsed_url.path),
                                            postdata,
                                            files,
                                            parsed_url.scheme == 'https')

        # Otherwise send a normal HTTP POST request
        else:
            encoded_postdata = None
            if postdata:
                encoded_postdata = urlencode(postdata)
            headers = [('Referer', self._referer),
                       ('User-Agent', self._useragent)]
            if compress:
                headers.append(('Accept-encoding', 'gzip'))

            handlers = self.get_handlers()
            opener = request.build_opener(*handlers)

            opener.addheaders = headers
            #print("***"+url)
            resp = opener.open(url, data=encoded_postdata.encode())
            resp_data = self._process_response(resp)

        # Parse the response into JSON
        if _log.isEnabledFor(logging.DEBUG):
            _log.debug('RESPONSE: ' + url + ', ' + _unicode_to_ascii(resp_data))
        #print(resp_data);
        if use_ordered_dict:
            resp_json = json.loads(resp_data, object_pairs_hook=OrderedDict)
        else:
            resp_json = json.loads(resp_data)

        # Convert to ascii if directed to do so
        if self.ensure_ascii and not use_ordered_dict:
            resp_json = _unicode_to_ascii(resp_json)

        # Check for errors, and handle the case where the token timed out
        # during use (and simply needs to be re-generated)
        try:
            if resp_json.get('error', None):

                errorcode = resp_json['error']['code'] if 'code' in resp_json['error'] else 0
                if errorcode == 498 and not is_retry:
                    _log.info('Token expired during post request, fetching a new '
                              + 'token and retrying')
                    self.logout()
                    newtoken = self.relogin()
                    postdata['token'] = newtoken
                    return self.post(path, postdata, files, ssl, compress,
                                     is_retry=True)
                elif errorcode == 498:
                    raise RuntimeError('Invalid token')
                self._handle_json_error(resp_json['error'])
                return None
        except AttributeError:
            # Top-level JSON object isnt a dict, so can't have an error
            pass

        return resp_json
    #----------------------------------------------------------------------
    def _postmultipart(self, host, selector, fields, files, ssl):
        boundary, body = self._encode_multipart_formdata(fields, files)
        headers = {
            'User-Agent': self._useragent,
            'Referer': self._referer,
            'Content-Type': 'multipart/form-data; boundary=%s' % boundary
        }

        if self.proxy_host:
            if ssl:
                h = http_client.HTTPSConnection(self.proxy_host, self.proxy_port,
                                                key_file=self.key_file,
                                                cert_file=self.cert_file)
                h.request('POST', 'https://' + host + selector, body, headers)
            else:
                h = http_client.HTTPConnection(self.proxy_host, self.proxy_port)
                h.request('POST', 'http://' + host + selector, body, headers)
        else:
            if ssl:
                h = http_client.HTTPSConnection(host, key_file=self.key_file,
                                                cert_file=self.cert_file)
                h.request('POST', selector, body, headers)
            else:
                h = http_client.HTTPConnection(host)
                h.request('POST', selector, body, headers)
        return h.getresponse().read()
    #----------------------------------------------------------------------
    def _encode_multipart_formdata(self, fields, files):
        boundary = self._make_boundary()
        buf = StringIO()
        for (key, value) in fields.items():
            buf.write('--%s\r\n' % boundary)
            buf.write('Content-Disposition: form-data; name="%s"' % key)
            buf.write('\r\n\r\n' + _tostr(value) + '\r\n')
        for (key, filepath, filename) in files:
            buf.write('--%s\r\n' % boundary)
            buf.write('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename))
            buf.write('Content-Type: %s\r\n' % (self._get_content_type(filename)))
            f = open(filepath, "rb")
            try:
                buf.write('\r\n' + f.read().decode('ISO-8859-1') + '\r\n')
            finally:
                f.close()
        buf.write('--' + boundary + '--\r\n\r\n')
        buf = buf.getvalue()
        return boundary, buf
    #----------------------------------------------------------------------
    def _get_content_type(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    #----------------------------------------------------------------------
    def _handle_json_error(self, error):
        _log.error(error.get('message', 'Unknown Error'))
        for errordetail in error['details']:
            _log.error(errordetail)


class _StrictURLopener(request.FancyURLopener):
    def http_error_default(self, url, fp, errcode, errmsg, headers):
        if errcode != 200:
            raise HTTPError(url, errcode, errmsg, headers, fp)

def _normalize_url(url, charset='utf-8'):
    """ Normalizes a URL. Based on http://code.google.com/p/url-normalize."""
    def _clean(string):
        string = str(unquote(string), 'utf-8', 'replace')
        return unicodedata.normalize('NFC', string).encode('utf-8')

    default_port = {
        'ftp': 21,
        'telnet': 23,
        'http': 80,
        'gopher': 70,
        'news': 119,
        'nntp': 119,
        'prospero': 191,
        'https': 443,
        'snews': 563,
        'snntp': 563,
    }

    # if there is no scheme use http as default scheme
    if url[0] not in ['/', '-'] and ':' not in url[:7]:
        url = 'http://' + url


    # shebang urls support
    url = url.replace('#!', '?_escaped_fragment_=')

    # splitting url to useful parts
    scheme, auth, path, query, fragment = urlsplit(url.strip())
    (userinfo, host, port) = re.search('([^@]*@)?([^:]*):?(.*)', auth).groups()

    # Always provide the URI scheme in lowercase characters.
    scheme = scheme.lower()

    # Always provide the host, if any, in lowercase characters.
    host = host.lower()
    if host and host[-1] == '.':
        host = host[:-1]
    # take care about IDN domains
    host = host.decode(charset).encode('idna')  # IDN -> ACE

    # Only perform percent-encoding where it is essential.
    # Always use uppercase A-through-F characters when percent-encoding.
    # All portions of the URI must be utf-8 encoded NFC from Unicode strings
    path = quote(_clean(path), "~:/?#[]@!$&'()*+,;=")
    fragment = quote(_clean(fragment), "~")

    # note care must be taken to only encode & and = characters as values
    query = "&".join(["=".join([quote(_clean(t), "~:/?#[]@!$'()*+,;=") \
                                for t in q.split("=", 1)]) for q in query.split("&")])

    # Prevent dot-segments appearing in non-relative URI paths.
    if scheme in ["", "http", "https", "ftp", "file"]:
        output = []
        for part in path.split('/'):
            if part == "":
                if not output:
                    output.append(part)
            elif part == ".":
                pass
            elif part == "..":
                if len(output) > 1:
                    output.pop()
            else:
                output.append(part)
        if part in ["", ".", ".."]:
            output.append("")
        path = '/'.join(output)

    # For schemes that define a default authority, use an empty authority if
    # the default is desired.
    if userinfo in ["@", ":@"]:
        userinfo = ""

    # For schemes that define an empty path to be equivalent to a path of "/",
    # use "/".
    if path == "" and scheme in ["http", "https", "ftp", "file"]:
        path = "/"

    # For schemes that define a port, use an empty port if the default is
    # desired
    if port and scheme in list(default_port.keys()):
        if port.isdigit():
            port = str(int(port))
            if int(port) == default_port[scheme]:
                port = ''

    # Put it all back together again
    auth = (userinfo or "") + host
    if port:
        auth += ":" + port
    if url.endswith("#") and query == "" and fragment == "":
        path += "#"
    return urlunsplit((scheme, auth, path, query, fragment))

def _parse_hostname(url, include_port=False):
    """ Parses the hostname out of a URL."""
    if url:
        parsed_url = urlparse((url))
        return parsed_url.netloc if include_port else parsed_url.hostname

def _is_http_url(url):
    if url:
        return urlparse(url).scheme in ['http', 'https']

def _unpack(obj_or_seq, key=None, flatten=False):
    """ Turns a list of single item dicts in a list of the dict's values."""

    # The trivial case (passed in None, return None)
    if not obj_or_seq:
        return None

    # We assume it's a sequence
    new_list = []
    for obj in obj_or_seq:
        value = _unpack_obj(obj, key, flatten)
        new_list.extend(value)

    return new_list

def _unpack_obj(obj, key=None, flatten=False):
    try:
        if key:
            value = [obj.get(key)]
        else:
            value = list(obj.values())
    except AttributeError:
        value = [obj]

    # Flatten any lists if directed to do so
    if value and flatten:
        value = [item for sublist in value for item in sublist]

    return value

def _unicode_to_ascii(data):
    """ Converts strings and collections of strings from unicode to ascii. """
    if isinstance(data, str):
        return _remove_non_ascii(data)
    if isinstance(data, str):
        return _remove_non_ascii(str(data.encode('utf8')))
    elif isinstance(data, collections.Mapping):
        return dict(list(map(_unicode_to_ascii, iter(data.items()))))
    elif isinstance(data, collections.Iterable):
        return type(data)(list(map(_unicode_to_ascii, data)))
    else:
        return data

def _remove_non_ascii(s):
    return ''.join(i for i in s if ord(i) < 128)

def _tostr(obj):
    if not obj:
        return ''
    if isinstance(obj, list):
        return ', '.join(map(_tostr, obj))
    return str(obj)




# This function is a workaround to deal with what's typically described as a
# problem with the web server closing a connection. This is problem
# experienced with www.arcgis.com (first encountered 12/13/2012). The problem
# and workaround is described here:
# http://bobrochel.blogspot.com/2010/11/bad-servers-chunked-encoding-and.html
def _patch_http_response_read(func):
    def inner(*args):
        try:
            return func(*args)
        except http_client.IncompleteRead as e:
            return e.partial

    return inner
http_client.HTTPResponse.read = _patch_http_response_read(http_client.HTTPResponse.read)
