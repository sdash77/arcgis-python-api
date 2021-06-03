class _Util:
    """
    Private class that provides wrapper functions for Connection objects
    (gis._con) xhr functions and some re-usable function endpoint calls
    for _start, _stop, _delete operations on a task
    """

    _gis = None
    _base_url = None
    _params = None

    def __init__(self, gis, base_url):
        """
        :param url: Base url of Velocity.
        :param gis: An authenticated arcigs.gis.GIS object.
        """
        self._gis = gis
        self._base_url = base_url
        self._params = {"authorization": f"token={gis._con.token}"}

    # ----------------------------------------------------------------------
    def _get_request(self, path):
        """
        Private wrapper function that  builds the absolute url from
        the base url + sub-path and then passing it to the xhr GET reqest
        gis._con.get(<url>, <params>)

        :param path: feeds | realtime | bigdata
        :return: Endpoint response
        """
        url = f"{self._base_url}{path}"
        response = self._gis._con.get(url, self._params)

        return self._parse_response(response)

    # ----------------------------------------------------------------------
    def _put_request(self, type, id, payload={}):
        """
        Private wrapper function that  builds the absolute url from
        the base url + sub-path and then passing it to the xhr PUT reqest
        gis._con.put(<url>, <params>, <payload>)

        :param path: feeds | realtime | bigdata
        :return: Endpoint response
        """
        path = f"{type}/{id}/"
        url = f'{self._base_url}{path}?{self._params.get("authorization")}'
        params = {**self._params, "data": payload}
        response = self._gis._con.put(url, params, post_json=True, try_json=False)

        return self._parse_response(response)

    # ----------------------------------------------------------------------
    def _post_request(self, type, id, payload={}):
        """
        Private wrapper function that  builds the absolute url from
        the base url + sub-path and then passing it to the xhr POST reqest
        gis._con.post(<url>, <params>, <payload>)

        :param path: feeds | realtime | bigdata
        :return: Endpoint response
        """
        path = f"{type}/{id}/"
        url = f'{self._base_url}{path}?{self._params.get("authorization")}'
        params = {**self._params, "data": payload}

        response = self._gis._con.post(url, params, post_json=True, try_json=True)

        return self._parse_response(response)

    # ----------------------------------------------------------------------
    def _delete_request(self, path):
        """
         Private wrapper function that  builds the absolute url from
        the base url + sub-path and then passing it to the xhr DELETE reqest
        gis._con.delete(<url>, <params>)

        :param path: feeds | realtime | bigdata
        :return: endpoint response
        """
        url = f"{self._base_url}{path}"
        response = self._gis._con.delete(url, self._params)

        return self._parse_response(response, return_boolean_for_success=True)

    # ----------------------------------------------------------------------
    def _get(self, type, id):
        """
         Generic task operation to get item by id
        :param type: feed | realtime | bigdata
        :param id: unique id of a task
        :return: Endpoint response for start task
        """
        path = f"{type}/{id}"
        return self._get_request(path)

    # ----------------------------------------------------------------------
    def _start(self, type, id):
        """
         Generic start task operation
        :param type: feed | realtime | bigdata
        :param id: unique id of a task
        :return: Endpoint response for start task
        """
        path = f"{type}/{id}/start"
        return self._get_request(path)

    # ----------------------------------------------------------------------
    def _stop(self, type, id):
        """
        Generic stop task operation
        :param type: feed | realtime | bigdata
        :param id: unique id of a task
        Return True if the task was successfully stopped.

        :returns: boolean
         a dictionary with error details.
        """
        path = f"{type}/{id}/stop"
        response = self._get_request(path)

        return response.get("status") == "success"

    # ----------------------------------------------------------------------
    def _status(self, type, id):
        """
        Generic get status task with possible taskTypes: feed | realtime | bigdata
        :param type: feed | realtime | bigdata
        :param id: unique id of a task
        :return: endpoint response for task status
        """
        path = f"{type}/{id}/status"
        return self._get_request(path)

    # ----------------------------------------------------------------------
    def _metrics(self, type, id):
        """
        Generic get metrics task with possible taskTypes: feed | realtime | bigdata
        :param type: feed | realtime | bigdata
        :param id: unique id of a task
        :return: endpoint response for task metrics
        """
        return self._post_request(type, id)

    # ----------------------------------------------------------------------
    def _delete(self, type, id):
        """
        :param type: feed | realtime | bigdata
        :param id: unique id of a task
        :return: A bool containing True (for success) or
         False (for failure) a dictionary with details is returned.
        """
        path = f"{type}/{id}"
        return self._delete_request(path)

    # ----------------------------------------------------------------------
    def _parse_response(self, response, return_boolean_for_success=False):
        """
        :param response: Result object of an endpoint
        :return: Result or raise exception if status has an 'error' attribute
        """
        if isinstance(response, dict) and response.get("status") == "error":
            raise Exception(response)
        elif isinstance(response, list):
            for item in response:
                if item.get("status") == "error":
                    raise Exception(item)
                else:
                    return response
        else:
            if return_boolean_for_success == True:
                return True
            else:
                return response
