import re


class _Util:
    """
    Private class that provides wrapper functions for Connection objects
    (gis._con) xhr functions and some re-usable function endpoint calls
    for _start, _stop, _delete operations on a task
    ==================     ====================================================================
    **Argument**           **Description**
    ------------------     --------------------------------------------------------------------
    gis                    An authenticated :class:`arcgis.gis.GIS` object.
    ------------------     --------------------------------------------------------------------
    base_url               Base url of Velocity.
    ==================     ====================================================================
    """

    _gis = None
    _base_url = None
    _params = None

    def __init__(self, gis, base_url):
        self._gis = gis
        self._base_url = base_url
        self._params = {"authorization": f"token={gis._con.token}"}


    def _get_request(self, path):
        """
        Private wrapper function that  builds the absolute url from
        the base url + sub-path and then passing it to the xhr GET request
        gis._con.get(<url>, <params>)

        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        path                   feeds | realtime | bigdata.
        ==================     ====================================================================

        :return: Endpoint response
        """
        url = f"{self._base_url}{path}"
        response = self._gis._con.get(url, self._params)

        return self._parse_response(response)


    def _put_request(self, task_type, id, payload=None):
        """
        Private wrapper function that  builds the absolute url from
        the base url + sub-path and then passing it to the xhr PUT request
        gis._con.put(<url>, <params>, <payload>)

        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        task_type              feeds | realtime | bigdata
        ------------------     --------------------------------------------------------------------
        id                     unique id of a task
        ------------------     --------------------------------------------------------------------
        **Optional Argument**  **Description**
        ------------------     --------------------------------------------------------------------
        payload                post body
        ==================     ====================================================================

        :return: Endpoint response
        """
        path = f"{task_type}/{id}/"
        url = f'{self._base_url}{path}?{self._params.get("authorization")}'

        if payload is None:
            payload = {}

        params = {**self._params, "data": payload}
        response = self._gis._con.put(url, params, post_json=True, try_json=False)

        return self._parse_response(response)


    def _post_request(self, task_type, id, payload=None, raise_error=True):
        """
        Private wrapper function that  builds the absolute url from
        the base url + sub-path and then passing it to the xhr POST request
        gis._con.post(<url>, <params>, <payload>)

        ======================     ====================================================================
        **Argument**               **Description**
        ----------------------     --------------------------------------------------------------------
        task_type                  feeds | realtime | bigdata
        ----------------------     --------------------------------------------------------------------
        id                         unique id of a task
        ----------------------     --------------------------------------------------------------------
        **Optional Argument**      **Description**
        ----------------------     --------------------------------------------------------------------
        payload                    post body
        ----------------------     --------------------------------------------------------------------
        raise_error                Default value - True.
        ======================     ====================================================================

        :return: Endpoint response
        """
        if id is not None:
            path = f"{task_type}/{id}/"
        else:
            path = f"{task_type}/"

        url = f'{self._base_url}{path}?{self._params.get("authorization")}'
        if payload is None:
            payload = {}

        params = {**self._params, "json": payload}

        response = self._gis._con.post(url, params, post_json=True, try_json=True)

        if raise_error is False:
            return response
        else:
            return self._parse_response(response)


    def _delete_request(self, path):
        """
        Private wrapper function that  builds the absolute url from
        the base url + sub-path and then passing it to the xhr DELETE reqest
        gis._con.delete(<url>, <params>)

        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        path                   feeds | realtime | bigdata.
        ==================     ====================================================================

        :return: Endpoint response
        """
        url = f"{self._base_url}{path}"
        response = self._gis._con.delete(url, self._params)

        return self._parse_response(response, return_boolean_for_success=True)


    def _get(self, task_type, id):
        """
        Generic task operation to get item by id

        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        task_type              feeds | realtime | bigdata
        ------------------     --------------------------------------------------------------------
        id                     unique id of a task
        ==================     ====================================================================

        :return: Endpoint response
        """
        path = f"{task_type}/{id}"
        return self._get_request(path)


    def _start(self, task_type, id):
        """
        Generic start task operation

        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        task_type              feeds | realtime | bigdata
        ------------------     --------------------------------------------------------------------
        id                     unique id of a task
        ==================     ====================================================================

        :return: Endpoint response
        """
        path = f"{task_type}/{id}/start"
        return self._get_request(path)


    def _stop(self, task_type, id):
        """
        Generic stop task operation

        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        task_type              feeds | realtime | bigdata
        ------------------     --------------------------------------------------------------------
        id                     unique id of a task
        ==================     ====================================================================

        :return: boolean
        """
        path = f"{task_type}/{id}/stop"
        response = self._get_request(path)

        return response.get("status") == "success"


    def _status(self, task_type, id):
        """
        Generic get status task with possible task types: feed | realtime | bigdata

        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        task_type              feeds | realtime | bigdata
        ------------------     --------------------------------------------------------------------
        id                     unique id of a task
        ==================     ====================================================================

        :return: endpoint response for task status
        """
        path = f"{task_type}/{id}/status"
        return self._get_request(path)


    def _metrics(self, task_type, id):
        """
        Generic get metrics task with possible task types: feed | realtime | bigdata

        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        task_type              feeds | realtime | bigdata
        ------------------     --------------------------------------------------------------------
        id                     unique id of a task
        ==================     ====================================================================

        :return: endpoint response for task metrics
        """
        return self._post_request(task_type, id)


    def _delete(self, task_type, id):
        """
        Generic task operation to delete item by id

        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        task_type              feeds | realtime | bigdata
        ------------------     --------------------------------------------------------------------
        id                     unique id of a task
        ==================     ====================================================================

        :return: A bool containing True (for success) or
         False (for failure) a dictionary with details is returned.
        """
        path = f"{task_type}/{id}"
        return self._delete_request(path)


    def _parse_response(self, response, return_boolean_for_success=False):
        """
        Generic task operation to get item by id

        ==========================      ====================================================================
        **Argument**                    **Description**
        --------------------------      --------------------------------------------------------------------
        response                        Result object of an endpoint
        --------------------------      --------------------------------------------------------------------
        return_boolean_for_success      Default value False
        ==========================      ====================================================================

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


    def _validate_response(self, response):
        if isinstance(response, dict) and response.get("status") == "error":
            return False
        elif isinstance(response, list):
            for item in response:
                if item.get("status") == "error":
                    return False
                else:
                    return True
        else:
            return True

    # ----------------------------------------------------------------------
    def sample_messages(self, input_type, payload=None):
        """
        Gets sample from a feed or source

        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        input_type             "feed" | "sources"
        ------------------     --------------------------------------------------------------------
        payload                payload for the sample message
        ==================     ====================================================================

        :return: Sample message response including derived schema and raw samples
        """
        if payload is None:
            raise AttributeError("Post request payload is empty")

        path = f"{input_type}/sampleMessages"
        _response = self._post_request(path, id=None, payload=payload)
        return _response

    # ----------------------------------------------------------------------
    def test_connection(self, input_type, payload=None):
        """
        Tests Connection to a feed, source, output

        ==================     ====================================================================
        **Argument**           **Description**
        ------------------     --------------------------------------------------------------------
        input_type             "feed" | "sources" | "outputs"
        ------------------     --------------------------------------------------------------------
        payload                payload for the feed
        ==================     ====================================================================

        :return: True if test connection is successfully else a dictionary with error details.
        """
        if payload is None:
           raise AttributeError("Post request payload is empty")

        path = f"{input_type}/testConnection"

        _response = self._post_request(
            path, id=None, payload=payload, raise_error=False
        )
        return self._validate_response(_response)

    def derive(self, sample_data: str, format_name: str = "Unknown"):
        if not sample_data:
            raise AttributeError("sample_data should not be empty")

        post_body = {
            "content": sample_data,
            "formatName": format_name,
            "properties": {}
        }
        response = self._post_request(
            task_type="schema/derive",
            id=None,
            payload=post_body,
            raise_error=False
        )
        return response

    def is_valid(self, label):
        pattern = "^[A-Za-z0-9_ ]*$"
        return bool(re.match(pattern, label))
