
import collections
import datetime
import inspect
import json
import re
import types

from arcgis.features import FeatureSet



def _call_generator(fnname, spec):
    """Generate GP function based on spec
    """
    varnames, defaults = zip(*spec)
    varnames = ('self', ) + varnames


    def call(self):
        """Method to invoke the Geoprocessing task"""
        #import sys
        kwargs = locals()
        kwargs.pop('self')
        self.__dict__.update(kwargs)

        # args, posargs = self.arguments()

        #print("My args: ")
        #for k, v in kwargs.items():
        #    print(k + " => " + str(v))

        return self._execute(kwargs)

    code = call.__code__
    new_code = types.CodeType(len(spec) + 1,
                              0,
                              len(spec) + 2,
                              code.co_stacksize,
                              code.co_flags,
                              code.co_code,
                              code.co_consts,
                              code.co_names,
                              varnames,
                              code.co_filename,
                              fnname,
                              code.co_firstlineno,
                              code.co_lnotab,
                              code.co_freevars,
                              code.co_cellvars)
    """
     * co_name gives the function name
     * co_argcount is the number of positional arguments (including
    arguments with default values)
     * co_nlocals is the number of local variables used by the function
    (including arguments)
     * co_varnames is a tuple containing the names of the local
    variables (starting with the argument names)
     * co_cellvars is a tuple containing the names of local variables
    that are referenced by nested functions
     * co_freevars is a tuple containing the names of free variables
     * co_code is a string representing the sequence of bytecode
    instructions
     * co_consts is a tuple containing the literals used by the bytecode
     * co_names is a tuple containing the names used by the bytecode
     * co_filename is the filename from which the code was compiled
     * co_firstlineno is the first line number of the function
     * co_lnotab is a string encoding the mapping from byte code offsets
    to line numbers (for details see the source code of the interpreter)
     * co_stacksize is the required stack size (including local
    variables)
     * co_flags is an integer encoding a number of flags for the
    interpreter.
    """




    return types.FunctionType(new_code,
                              {"__builtins__": __builtins__},
                              argdefs=defaults)

class GeoprocessingTool(collections.OrderedDict):
    "A geoprocessing tool."
    def __init__(self, item):
        """
        Constructs a Geoprocessing tool given it's item from the GIS
        """
        if item.type.lower() != 'geoprocessing service':
            raise TypeError("item type must be geoprocessing service")
        self.item = item
        self.url = self.item.url
        self._taskurls = {}
        self._method_params = {}

        print("URL: " + self.url)
        params = {
            "f" : "json"
        }
        svcprops = self.item._portal.con.post(self.url, params,  use_ordered_dict=True)
        collections.OrderedDict.__init__(self, svcprops)
        for task in svcprops['tasks']:
            print("Task: " + task)
            fnname = self._camelCase_to_underscore(task)

            taskurl = self.url + "/" + task

            self._taskurls[fnname] = taskurl + "/execute"

            taskprops = self.item._portal.con.post(taskurl, params)
            execution_type = taskprops['executionType']
            task_params = taskprops['parameters']

            helpstring = taskprops["displayName"] + "\n"
            if 'docstring' in taskprops:
                helpstring = helpstring + ". " + taskprops['docstring'] + "\nParameters:\n"


            spec = []
            name_type = {}
            for param in task_params:

                param_name = param['name']

                param_type = param['dataType']
                param_dval = param['defaultValue']
                param_drtn = param['direction']

                param_rqrd = param['parameterType']

                if param_type == 'GPFeatureRecordSetLayer':
                    param_dval = None

                py_param_type_ = param_type
                if param_type == 'GPBoolean':
                    py_param_type_ = bool
                elif param_type == 'GPDouble':
                    py_param_type_ = float
                elif param_type == 'GPLong':
                    py_param_type_ = int
                elif param_type == 'GPString':
                    py_param_type_ = str
                elif param_type == 'GPDate':
                    py_param_type_ = datetime.date
                else:
                    py_param_type_ = param_type


                """
                GPDataFile	DataFile
                GPFeatureRecordSetLayer	FeatureSet
                GPLinearUnit	LinearUnit
                GPRasterData	RasterData
                GPRasterLayer	RasterData
                GPRecordSet	FeatureSet
                """

                if param_drtn == 'esriGPParameterDirectionInput':
                    name_type[param_name] = py_param_type_
                    print(param_name + " : " + param_type)
                    #if param_dval is not None and param_dval != '':
                    #    print(" = " + str(param_dval))
                    if param_rqrd is not None and param_rqrd == 'esriGPParameterTypeOptional':
                        print(" = None")
                    param_spec = ( param_name , param_dval )
                    spec.append(param_spec)

                    helpstring = helpstring + "   " + param_name + ": " + param['displayName']  + " (" + str(py_param_type_) + ")"
                    if param_rqrd == 'esriGPParameterTypeOptional':
                        helpstring = helpstring + " Optional parameter. "
                    elif param_rqrd == 'esriGPParameterTypeRequired':
                        helpstring = helpstring + " Required parameter. "

                    if 'description' in param:
                        helpstring = helpstring + param['description']

                elif param_drtn == 'esriGPParameterDirectionOutput':
                    name_type['return'] = py_param_type_

                    helpstring = helpstring + "\nReturns " + param['displayName'] + "(" + str(py_param_type_) + ")"

                helpstring = helpstring + "\n"

            if 'helpUrl' in taskprops:
                helpstring = helpstring + "\nSee " + taskprops['helpUrl'] + " for additional help."

            generatedfn = _call_generator(task, spec)
            generatedfn.__annotations__ = name_type
            generatedfn.__doc__ = helpstring

            setattr(self, fnname, types.MethodType(generatedfn, self))

            self._method_params[task] = name_type

        # http://www.arcgis.com/home/item.html?id=383c2039b89d43baa0010c3bf243b144
        # http://sampleserver1.arcgisonline.com/ArcGIS/rest/Services/Specialty/ESRI_Currents_World/GPServer

    def __str__(self):
         return json.dumps(self)

    def _execute(self, params):
        caller_fnname = inspect.stack()[1][3]
        url = self.url + "/" + caller_fnname + "/execute"
        #print("Will call " + url +  " with these parameters:")

        name_type = self._method_params[caller_fnname]

        params.update({ "f" : "json" })

        #---------------------in---------------------#
        """
        for k, v in params.items():
            #print(k + " = " + str(v))
            if k in name_type:
                py_type = name_type[k]
                if py_type == 'GPFeatureRecordSetLayer':
                    # if passed in geometries but require featureset, create one
                    geometry = v
                    val = {}
                    val['geometryType'] = 'esriGeometryPoint'
                    val['features'] = [{"geometry" : geometry}]
                    val['sr'] = {"wkid":102100,"latestWkid":3857}
                    params[k] = val
        """
        #--------------------------------------------#
        resp = self.item._portal.con.post(url, params)
        #--------------------------------------------#

        ret_type = name_type['return']
        #try:
        if 1==1:
            geometries = []

            #--------------------out---------------------#
            # if FeatureSet, return FeatureSet... and let map.draw draw features from featureset
            if ret_type == 'GPFeatureRecordSetLayer':
                #print("RESP IN GP:"+str(resp))
                #resp = {"results":[{"paramName":"Output","dataType":"GPFeatureRecordSetLayer","value":{"geometryType":"esriGeometryPolyline","spatialReference":{"wkid":4326},"features":[{"attributes":{"FID":1,"FNODE_":0,"Shape_Length":32.794529279575883},"geometry":{"paths":[[[84.8748779296875,-5.9821438789367676],[85.697532653808594,-6.5506825447082448],[85.362907409667969,-7.493033885955807],[84.996139526367188,-8.423344612121582],[84.110282897949219,-8.8873043060302734],[83.259567260742188,-9.4129314422607422],[82.274673461914063,-9.5861167907714808],[81.274681091308594,-9.582554817199707],[80.277946472167969,-9.6632461547851562],[79.287498474121094,-9.8011550903320312],[78.3453369140625,-10.136309623718265],[77.481758117675781,-10.640528678894043],[76.563209533691406,-11.035839080810547],[75.613388061523438,-11.348619461059567],[74.674003601074219,-11.691491127014157],[73.757270812988281,-12.090988159179688],[72.79632568359375,-12.367743492126465],[71.802711486816406,-12.480551719665527],[70.901077270507813,-12.913044929504391],[70.1573486328125,-13.581530570983887],[69.268287658691406,-14.039313316345215],[68.351539611816406,-14.438780784606934],[67.512741088867188,-14.983222007751465],[66.603912353515625,-15.400397300720215],[65.611618041992188,-15.276482582092285],[64.64862060546875,-15.006984710693359],[63.674091339111328,-14.782718658447262],[62.679428100585938,-14.885892868041989],[61.699390411376953,-15.084704399108883],[60.713626861572266,-15.252829551696777],[59.714076995849609,-15.22271728515625],[58.786506652832031,-14.849072456359863],[57.924812316894531,-14.341644287109375],[57.436767578125,-13.838002204895016],[57.370742797851563,-13.777911186218258],[57.367759704589844,-13.775339126586911]]]}}],"exceededTransferLimit":False}}],"messages":[]}

                value = resp['results'][0]['value']
                featset = FeatureSet.from_dict(value)
                return featset

                #    geometries.append(geometry)
            else:
                print("NOT FS")

            return resp['results'][0]['value']
        #except:
        #    print("Error: " + str(resp))
        #    return resp


    def execute(self, task, input,
                outSR=None,
                processSR=None,
                returnZ=False,
                returnM=False):

        # http://sampleserver1.arcgisonline.com/ArcGIS/rest/services/Specialty/ESRI_Currents_World/GPServer/MessageInABottle/execute? Input_Point={"features":[{"geometry":{"x":0,"y":0}}]}& Days=50
        url = self.url + "/" + task + "/execute"
        params = {
            "f" : "json",
        }

        if outSR is not None:
            params['outSR'] = outSR
        if processSR is not None:
            params['processSR'] = processSR
        if returnZ:
            params['returnZ'] = "true"
        if returnM:
            params['returnM'] = "true"

        for k, v in input.items():
            params[k] = v

        resp = self.item._portal.con.post(url, params)
        return resp

    def _camelCase_to_underscore(self, name):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
