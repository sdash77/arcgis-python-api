import os
import sys
import logging as _logging
import urllib.parse
import concurrent.futures
from types import MethodType

from arcgis.auth.tools import LazyLoader
from arcgis.gis import GIS
from arcgis import env

arcgis = LazyLoader("arcgis")
_mixins = LazyLoader("arcgis._impl.common._mixins")
from datetime import datetime
from arcgis.features import FeatureSet
from arcgis.mapping import MapImageLayer
from arcgis.geoprocessing import DataFile, LinearUnit, RasterData
from arcgis.geoprocessing._support import _execute_gp_tool
from arcgis.geoprocessing._tool import (
    _camelCase_to_underscore,
    _generate_param,
    _inspect_tool,
)

_log = _logging.getLogger(__name__)

###########################################################################
def _input_string_params(spec, name_type, name_param, num_spaces=20):
    """creates the input strings for the lambda"""
    src_code = ""
    param_inputs = ""
    if len(spec) > 0:
        param_name, param_dval = spec[0]
        param_type = name_type[param_name]

        src_code += _generate_param(name_param, param_dval, param_name, param_type)
        param_inputs += f"{param_name}={param_name},"

        for param_name_dval in spec[1:]:  # [ (param_name, param_dval) ]
            param_name, param_dval = param_name_dval
            param_type = name_type[param_name]
            src_code += ","
            src_code += _generate_param(name_param, param_dval, param_name, param_type)
            param_inputs += f"{param_name}={param_name},"
        src_code += ","
    src_code += ""
    return src_code, param_inputs


###########################################################################
def _build_lambda(self, input_strings, param_inputs):
    """builds the lambda"""
    return eval(
        f"lambda self, {input_strings}: self._run_tool({param_inputs})".replace(
            "\n", ""
        )
        .replace('''"""''', "'")
        .replace(":str", "")
    )


###########################################################################
class GPTask:
    """
    The GP Task resource represents a single task in a geoprocessing
    service published using ArcGIS Server. It provides basic information
    about the task including its name and display name. It also provides
    detailed information about the various input and output parameters
    exposed by the task.
    """

    _gis = None
    _url = None
    _parent = None
    _properties = None

    def __init__(
        self,
        url: str,
        parent: "GPService",
        gis: GIS = None,
    ):
        self._parent = parent
        self._url = url
        if gis is None and env.active_gis is None:
            gis = GIS()
        elif gis is None and env.active_gis:
            gis = env.active_gis
        self._gis = gis
        name = self.properties["name"]
        uses_map_as_result = self._parent.properties.resultMapServerName != ""

        (
            helpstring,
            name_name,
            name_type,
            return_values,
            spec,
            name_param,
            choice_list_db_param,
        ) = _inspect_tool(self.properties, uses_map_as_result)
        param_db = {}
        for param_name_dval in spec:  # [ (param_name, param_dval) ]
            param_name, param_dval = param_name_dval
            param_type = name_type[param_name]
            gp_param_name = name_name[param_name]
            param_db[param_name] = (param_type.__name__, gp_param_name)
        return_values2 = []
        for retval in return_values:
            param_db[retval["name"]] = (retval["type"].__name__, retval["display_name"])
            return_values2.append(
                {
                    "name": retval["name"],
                    "display_name": retval["display_name"],
                    "type": retval["type"].__name__,
                }
            )
        self._return_values = return_values2
        input_string, param_string = _input_string_params(spec, name_type, name_param)
        self._param_db = param_db
        l = _build_lambda(
            self=self, input_strings=input_string, param_inputs=param_string
        )
        l.__doc__ = helpstring

        setattr(self, _camelCase_to_underscore(name), MethodType(l, self))

    def _run_tool(self, **kwargs):
        """runs the tool"""
        future = True
        param_db = self._param_db
        return_values = self._return_values
        run_async = (
            self._parent.properties["executionType"] != "esriExecutionTypeSynchronous"
        )
        return _execute_gp_tool(
            self._gis,
            os.path.basename(self._url),
            kwargs,
            param_db,
            return_values,
            run_async,
            os.path.dirname(self._url),
            future=future,
        )

    # ----------------------------------------------------------------------
    @property
    def properties(self) -> dict:
        """
        Returns the Service's Properties

        :return: dict
        """
        if self._properties is None:

            params = {"f": "json"}
            self._properties = self._gis._con.get(self._url, params)
        return _mixins.PropertyMap(self._properties)

    # ----------------------------------------------------------------------
    def __str__(self):
        return f"<{self.__class__.__name__} @ {self._url}>"

    # ----------------------------------------------------------------------
    def __repr__(self):
        return self.__str__()


###########################################################################
class GPService:
    """
    A geoprocessing service can contain one or more tools that use input
    data from a client application, process it, and return output in the
    form of features, maps, reports, files, or services. These tools are
    first authored and run in ArcGIS Pro or ArcGIS Desktop, typically as
    a custom model or script tools, before being shared to an ArcGIS
    Server.
    """

    _gis = None
    _url = None
    _tasks = None
    _properties = None
    # ----------------------------------------------------------------------
    def __init__(self, url: str, gis: GIS = None):
        self._url = url
        if gis is None and env.active_gis is None:
            gis = GIS()
        elif gis is None and env.active_gis:
            gis = env.active_gis
        self._gis = gis

    # ----------------------------------------------------------------------
    def __str__(self):
        return f"<{self.__class__.__name__} @ {self._url}>"

    # ----------------------------------------------------------------------
    def __repr__(self):
        return self.__str__()

    # ----------------------------------------------------------------------
    @property
    def properties(self) -> dict:
        """
        Returns the Service's Properties

        :return: dict
        """
        if self._properties is None:

            params = {"f": "json"}
            self._properties = _mixins.PropertyMap(
                self._gis._con.get(self._url, params)
            )
        return self._properties

    # ----------------------------------------------------------------------
    @property
    def tasks(self) -> list:
        """returns the GP Tasks"""
        if self._tasks is None:
            self._tasks = [
                GPTask(
                    url=self._url + urllib.parse.quote(f"/{task}"),
                    gis=self._gis,
                    parent=self,
                )
                for task in self.properties["tasks"]
            ]
        return self._tasks

    # ----------------------------------------------------------------------
    def refresh(self):
        """
        Reloads the Service Information
        """
        self._tasks = None
        self._properties = None
