import os
from arcgis.gis import GIS
from arcgis._impl.common._mixins import PropertyMap

########################################################################
class NotebookManager(object):
    """
    """
    _url = None
    _gis = None
    _properties = None
    #----------------------------------------------------------------------
    def __init__(self, url, gis):
        """Constructor"""
        self._url = url
        if isinstance(gis, GIS):
            self._gis = gis
            self._con = self._gis._con
        else:
            raise ValueError("Invalid GIS object")
    #----------------------------------------------------------------------
    def _init(self):
        """loads the properties"""
        try:
            params = {'f': 'json'}
            res = self._gis._con.get(self._url, params)
            self._properties = PropertyMap(res)
        except:
            self._properties = PropertyMap({})
    #----------------------------------------------------------------------
    def __str__(self):
        return "<NotebookManager @ {url}>".format(url=self._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return "<NotebookManager @ {url}>".format(url=self._url)
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """returns the properties of the resource"""
        if self._properties is None:
            self._init()
        return self._properties
    #----------------------------------------------------------------------
    @property
    def runtimes(self):
        """
        Returns a list of all runtimes

        :return: List
        """
        url = self._url + "/runtimes"
        params = {'f' : 'json'}
        res = self._con.get(url, params)
        if "runtimes" in res:
            return [Runtime(url=url + "/rid".format(rid=r["id"]),
                            gis=self._gis) \
                    for r in res["runtimes"]]
        return []
    #----------------------------------------------------------------------
    def restore_runtime(self):
        """
        This operation restores the two default notebook runtimes in ArcGIS
        Notebook Server - ArcGIS Notebook Python 3 Standard and ArcGIS
        Notebook Python 3 Advanced - to their original settings.
        """
        url = self._url + "/runtimes/restore"
        params = {'f' : 'json'}
        res = self._con.post(url, params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    def _register(self):
        """"""
        raise NotImplementedError("Register is not implemented yet")

########################################################################
class Runtime(object):
    """
    """
    _url = None
    _gis = None
    _properties = None
    #----------------------------------------------------------------------
    def __init__(self, url, gis):
        """Constructor"""
        self._url = url
        if isinstance(gis, GIS):
            self._gis = gis
            self._con = self._gis._con
        else:
            raise ValueError("Invalid GIS object")
    #----------------------------------------------------------------------
    def _init(self):
        """loads the properties"""
        try:
            params = {'f': 'json'}
            res = self._gis._con.get(self._url, params)
            self._properties = PropertyMap(res)
        except:
            self._properties = PropertyMap({})
    #----------------------------------------------------------------------
    def __str__(self):
        return "<Runtime @ {url}>".format(url=self._url)
    #----------------------------------------------------------------------
    def __repr__(self):
        return "<Runtime @ {url}>".format(url=self._url)
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """returns the properties of the resource"""
        if self._properties is None:
            self._init()
        return self._properties
    #----------------------------------------------------------------------
    def delete(self):
        """
        Deletes the current runtime from the ArcGIS Notebook Server

        :returns: boolean

        """
        url = self._url + "/unregister"
        params = {'f' : 'json'}
        res = self._con.post(url, params)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    def update(self,
               name=None,
               image_id=None,
               max_cpu=None,
               max_memory=None,
               memory_unit=None,
               max_swap_memory=None,
               swap_memory_unit=None,
               shared_memory=None,
               docker_runtime=None,
               shared_unit=None,
               version=None,
               container_type=None,
               pull_string=None,
               require_advanced_priv=None):
        """
        This operation allows you to update the properties of a notebook
        runtime in ArcGIS Notebook Server. These settings will be applied
        to every container to which the runtime is applied.

        You can use this operation to update the resource limits of the
        runtime, such as maximum CPU and maximum memory. You can also use
        it to extend either of the default notebook runtimes, in order to
        make additional Python modules available to your notebook authors,
        or as a step in making ArcGIS Notebook Server able to use graphical
        processing units (GPUs).



        """
        file = {'manifestFile' : manifest}
        params = {
            "name": name,
            "version" : version,
            "imageId" : image_id,
            "containerType": container_type,
            "imagePullString" : pull_string,
            "requiresAdvancedPrivileges": require_advanced_priv,
            "maxCpu" : max_cpu,
            "maxMemory" : max_memory,
            "maxMemoryUnit" : memory_unit,
            "maxSwapMemory" : max_swap_memory,
            "maxSwapMemoryUnit" : swap_memory_unit,
            "sharedMemory" : shared_memory,
            "sharedMemoryUnit" : shared_unit,
            "dockerRuntime": docker_runtime,
            'f' : 'json'
        }
        if k in list(params.keys()):
            if params[k] is None:
                del params[k]
        if len(params) == 1:
            return False
        res = self._con.post(url, params, files=file)
        if 'status' in res:
            return res['status'] == 'success'
        return res
    #----------------------------------------------------------------------
    def manifest(self):
        """"""
        url = self._url + "/manifest"
        params = {'f' : 'json'}
        res = self._con.get(url, params)
        if "libraries" in res:
            return res["libraries"]
        return res



