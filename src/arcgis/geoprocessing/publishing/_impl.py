import os
import sys
import json
import types
import typing
import inspect
import tempfile
from ._mappings import _mapping
from ._template import pyttemplate, xmltemplate

import dill
from dill.detect import globalvars

def create_toolbox(func, toolbox=None, out_folder=None):
    """
    Creates a Python Toolbox from a method.


    The function given must use typings or an exception will be raised.
    See: https://docs.python.org/3/library/typing.html


    ===============     ====================================================================
    **Argument**        **Description**
    ---------------     --------------------------------------------------------------------
    func                Required Python Function.  The method to add to a python toolbox
    ---------------     --------------------------------------------------------------------
    toolbox             Option String. The name of the toolbox
    ---------------     --------------------------------------------------------------------
    out_folder          Optional string. Save location for the toolbox.
    ===============     ====================================================================


    :return: string, string

    The first string is the path to the toolbox file, and the second string is the
    path to the xml file.

    """
    if len(func.__annotations__) == 0:
        raise ValueError("Annotations must be used.")
    if out_folder is None:
        out_folder = tempfile.gettempdir()
    elif os.path.isdir(out_folder) == False:
        os.makedirs(out_folder, exist_ok=True)
    if toolbox is None:
        toolbox = func.__name__+ "Toolbox"
    source = inspect.getsource(func).strip()

    tool = func.__name__+ "Tool"

    x = xmltemplate.format(tool=tool, toolbox=toolbox)
    xmlfile = os.path.join(out_folder, "%s.pyt.xml" % toolbox)
    pytfile = os.path.join(out_folder, "%s.pyt" % toolbox)
    params, input_index, set_order = _create_parameter_mapping(func)
    f = dill.loads(dill.dumps(func))
    source = inspect.getsource(f)
    ins = []
    for k,v in input_index.items():
        ins.append("'{key}' : parameters[{idx}].value".format(key=k, idx=v))
    ins = "{%s}" % ",".join(ins)
    use = "            func = %s\n" % func.__name__
    use += "            res = func(**{params})\n".format(params=ins)
    use += "            set_order = %s\n" % set_order
    use += "            if isinstance(res, arcpy.Result):\n"
    use += "                for idx, r in enumerate(res):\n"
    use += "                    arcpy.SetParameterAsText(set_order[idx], r)\n"
    use += "            elif isinstance(res, (tuple, list)):\n"
    use += "                for idx, r in enumerate(res):\n"
    use += "                    arcpy.SetParameterAsText(set_order[idx], r)\n"
    use += "            elif len(set_order) == 1:\n"
    use += "                arcpy.SetParameterAsText(set_order[0], res)\n"
    use += "            else:\n"
    use += "                arcpy.AddMessage(\"No Output Parameters are Defined.\")    \n"

    t = pyttemplate.format(tool=tool,
                           toolbox=toolbox,
                           imports="", # place holder for additional imports
                           parameters=params,
                           code=source,
                           use=use)

    open(xmlfile, 'w').write(x)
    open(pytfile, 'w').write(t)
    return pytfile, xmlfile

def _create_parameter_mapping(func):
    """
    Creates the Python Toolbox input/output parameters from a function.

    The function given must use typings or an exception will be raised.
    See: https://docs.python.org/3/library/typing.html

    ===============     ====================================================================
    **Argument**        **Description**
    ---------------     --------------------------------------------------------------------
    func                Required Python Function.  The method to add to a python toolbox
    ===============     ====================================================================


    :return: string, dict, list

    """
    name = func.__name__
    asp = inspect.getfullargspec(func)
    sig = inspect.signature(func)
    annotations = func.__annotations__
    input_order = {} # 'function param : index
    set_index = []
    params = []
    pns = []
    count = 0
    if len(annotations) == 0 and len(asp) > 0:
        raise ValueError("Python function {name} must use annotations".format(name=name))
    for arg in asp.args:
        varname = "param%s" % count
        input_order[arg] = count
        pt = "Required"
        if arg in sig.parameters and\
           sig.parameters[arg]._default != inspect._empty:
            pt = "Optional"
        params.append("""        {varname} = arcpy.Parameter(
            displayName=\"{arg}\",
            name=\"{arg}\",
            datatype=\"{mapping}\",
            parameterType=\"{pt}\",
            direction="Input")""".format(arg=arg, varname=varname, pt=pt, mapping=_mapping[func.__annotations__[arg]]))

        pns.append(varname)
        if arg in sig.parameters and\
           sig.parameters[arg]._default != inspect._empty:
            default = sig.parameters[arg].default
            if isinstance(default, (int, float)):
                params.append("        {varname}.value = {default}".format(varname=varname, default=default))
            else:
                params.append("        {varname}.value = '{default}'".format(varname=varname, default=default))
        count += 1
    if 'return' in annotations:

        if func.__annotations__['return'] == typing.TupleMeta or \
           func.__annotations__['return'] == typing.Tuple or \
           isinstance(func.__annotations__['return'], (typing.Tuple, typing.TupleMeta)):
            rcount = 0
            for t in func.__annotations__['return'].__args__:
                varname = "param%s" % count
                arg = "output_%s" % rcount
                params.append(
                    """        {varname} = arcpy.Parameter(
                    displayName=\"{arg}\",
                    name=\"{arg}\",
                    datatype=\"{mapping}\",
                     parameterType=\"Derived\",
                     direction=\"Output\")""".format(arg=arg, varname=varname, mapping=_mapping[t]))
                count += 1
                rcount += 1
                pns.append(varname)
                set_index.append(count)
        else:
            rcount = 0
            varname = "param%s" % count
            arg = "output_%s" % rcount
            params.append(
                """        {varname} = arcpy.Parameter(
                displayName='{arg}',
                name='{arg}',
                datatype='{mapping}',
                parameterType="Derived",
                direction="Output")""".format(arg=arg, varname=varname, mapping=_mapping[func.__annotations__['return']]))
            pns.append(varname)
            set_index.append(count)
    params.append("        params = [{p}]".format(p=", ".join(pns)))
    return "\n".join(params), input_order, set_index
