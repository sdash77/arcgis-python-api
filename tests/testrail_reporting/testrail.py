#
# TestRail API binding for Python 3.x (API v2, available since 
# TestRail 3.0)
#
# Learn more:
#
# http://docs.gurock.com/testrail-api2/start
# http://docs.gurock.com/testrail-api2/accessing
#
# Copyright Gurock Software GmbH. See license.md for details.
#

import urllib.request, urllib.error
import json, base64
import time
import ssl

retries = 3

class APIClient:
	def __init__(self, base_url):
		self.user = ''
		self.password = ''
		if not base_url.endswith('/'):
			base_url += '/'
		self.__url = base_url + 'index.php?/api/v2/'

	#
	# Send Get
	#
	# Issues a GET request (read) against the API and returns the result
	# (as Python dict).
	#
	# Arguments:
	#
	# uri                 The API method to call including parameters
	#                     (e.g. get_case/1)
	#
	def send_get(self, uri):
		return self.__send_request('GET', uri, None)

	#
	# Send POST
	#
	# Issues a POST request (write) against the API and returns the result
	# (as Python dict).
	#
	# Arguments:
	#
	# uri                 The API method to call including parameters
	#                     (e.g. add_case/1)
	# data                The data to submit as part of the request (as
	#                     Python dict, strings must be UTF-8 encoded)
	#
	def send_post(self, uri, data):
		return self.__send_request('POST', uri, data)

	def __send_request(self, method, uri, data):
		url = self.__url + uri
		#time.sleep(1)
		#print('URL: ' + url + ' After 1 second')
		request = urllib.request.Request(url)
		if (method == 'POST'):
			request.data = bytes(json.dumps(data), 'utf-8')
		auth = str(
			base64.b64encode(
				bytes('%s:%s' % (self.user, self.password), 'utf-8')
			),
			'ascii'
		).strip()
		request.add_header('Authorization', 'Basic %s' % auth)
		request.add_header('Content-Type', 'application/json')
		context = ssl._create_unverified_context()
		for attempt in range(retries):
			e = None
			try:
				response = urllib.request.urlopen(request, context=context, timeout=10).read()
			except urllib.error.HTTPError as ex:
				if ex.code == 409 or ex.code == 429:
					if ex.code == 409:
						print("TestRails is in maintainance mode. Retrying in 120 seconds...")
					else:
						print("Received 429 (Too Many Requests) response. Retrying in 120 seconds...")
					time.sleep(120)
					continue  # Retry the request
				response = ex.read()
				e = ex

			if response:
				result = json.loads(response.decode())
			else:
				result = {}

			if e != None:
				if result and 'error' in result:
					error = '"' + result['error'] + '"'
				else:
					error = 'No additional error message received'
				raise APIError('TestRail API returned HTTP %s (%s)' % 
					(e.code, error))

			return result
		raise APIError('Maximum retries exceeded')
	
class APIError(Exception):
	pass
