"""
Creates renderer dictionaries that can be used to help visualize webmap content
"""

import json

import pandas as pd
import numpy as np
import pysal as ps
import matplotlib.pyplot as plt

import arcgis
from arcgis._impl.common._utils import chunks
from arcgis.features import FeatureCollection, FeatureSet, SpatialDataFrame
from arcgis.gis import GIS
from arcgis.geometry import _types

from arcgis.features._data.geodataset.___viz.symbol import create_symbol, _cmap2rgb

__all__ = ['render']

RENDERER_TYPES = {
    "s" : 'simple',#
    "u" : 'unique',#
    'h' : 'heatmap',#
    'c' : 'ClassBreaks',#
    #"p" : 'Predominance',
    'str' : 'Stretch',#
    't' : "Temporal",#
    'v' : "vector field"#
}

def render(sdf_or_series,
           label=None,
           render_type=None,
           cmap=None,
           **symbol_args):
    renderer = None
    if render_type is None:
        render_type = 's'
    elif render_type.lower() not in RENDERER_TYPES:
        raise Exception("Invalid Renderer type.")
    else:
        render_type = render_type.lower()
    if render_type == 's':
        symbol = symbol_args.pop('symbol', None)
        if symbol is None:
            symbol = create_symbol(
                geometry_type=sdf_or_series.geometry_type.lower(),
                symbol_type=symbol_args.pop('symbol_type', None),
                symbol_style=symbol_args.pop('symbol_style', None),
                cmap=cmap,
                **symbol_args)
        renderer = {
            "type" : "simple",
            'label' : label,
            "description" : symbol_args.pop('description', ""),
            "rotationExpression" : symbol_args.pop("rotation_expression", ""),
            "rotationType" : symbol_args.pop("rotation_type", 'arithmetic'),
            "visualVariables" : symbol_args.pop("visual_variables", None),
            "symbol" : symbol
        }
        return renderer
    elif renderer_type.lower() == "h":
        colorStops = []
        field = symbol_args.pop('field', None)
        stops = symbol_args.pop('stops', 2)
        ratio = symbol_args.pop('ratio', .01)
        maxPixelIntensity = symbol_args.pop('max_intensity', 10000)
        minPixelIntensity = symbol_args.pop('max_intensity', 0)
        r = 0
        for cstep in np.linspace(0,255,
                                 num=stops,
                                 dtype=np.int).tolist():
            colorStops.append(
                {
                    'ratio' : r,
                    'color' : _cmap2rgb(cmap=cmap, cstep=cstep)
                }
            )
            r += ratio
            del cstep
        renderer = {
            'type' : 'heatmap',
            'blurRadius' : symbol_args.pop('blur_radius', 10),
            "maxPixelIntensity" : maxPixelIntensity,
            "minPixelIntensity" : minPixelIntensity,
            "colorStops" : colorStops
        }
        return renderer
    elif render_type == 'u':

        default_symbol = symbol_args.pop('default_symbol', None)
        if default_symbol is None:
            default_symbol = create_symbol(
                geometry_type=sdf_or_series.geometry_type.lower(),
                symbol_type=symbol_args.pop('symbol_type', None),
                symbol_style=symbol_args.pop('symbol_style', None),
                cmap=cmap,
                **symbol_args)
        field1 = symbol_args.pop("field1", None)
        if field1 is None:
            raise ValueError("You must provide a single field name to use unique value renderer as field1='columnname'")
        fields = symbol_args.pop('fields', None)
        if isinstance(fields, str):
            fields = [fields]
        field_delimiter = symbol_args.pop('field_delimiter', ',')
        rotation_expression = symbol_args.pop("rotation_expression", None)
        rotation_type = symbol_args.pop("rotation_type", "arithmetic")

        renderer = {
            "type" : "uniqueValue",
            "defaultLabel" : symbol_args.pop('default_label', "Other"),
            "defaultSymbol" : default_symbol,
            "fieldDelimiter" : field_delimiter,
            "rotationExpression" : rotation_expression,
            "rotationType" : rotation_type,
            "valueExpression" : symbol_args.pop("arcade_expression", None),
            "valueExpressionTitle" : symbol_args.pop("arcade_title", None),
            "visualVariable" : symbol_args.pop('visual_variable', None)
        }
        c = 1
        for f in fields:
            renderer['field%s' % c] = f
            c += 1
        if len(fields) == 1:
            uvals = sdf_or_series[fields[0]].unique().tolist()
        else:
            uvals = sdf_or_series.groupby(fields).size().reset_index().rename(
                columns={0:'count'}).drop(columns='count').tolist()
            uvals2 = []
            for r in uvals:
                row = []
                for i in r:
                    row.append(str(i))
                uvals2.append(",".join(row))
                del r
            uvals = uvals2
        if len(uvals) > 10:
            uvals = uvals[:10]
        unique_values = []
        st = symbol_args.pop('symbol_type', None)
        ss = symbol_args.pop('symbol_style', None)
        for uval in uvals:
            unique_values.append({
                "value" : uval,
                "label" : uval,
                "description" : "",
                "symbol" : create_symbol(
                geometry_type=sdf_or_series.geometry_type.lower(),
                symbol_type=st,
                symbol_style=ss,
                cmap=cmap,
                **symbol_args)
            })
        renderer['uniqueValueInfos'] = unique_values
    elif renderer_type == "v":
        renderer = {
            'type' : 'vectorField',
            'visualVariable' : symbol_args.pop('visual_variable', None),
            'style' : symbol_args.pop('style'),
            'rotationType' : symbol_args.pop('rotation_type', 'arithmetic'),
            'flowRepresentation' : symbol_args.pop('flow', 'flow_from'),
            'attributeField' : symbol_args.pop('attribute_field', None)
        }
    elif renderer_type == "c":
        class_count = symbol_args.pop('class_count', 3) # number of classess for class break

        renderer = {
            "type" : "classBreaks",
            "valueExpression" : symbol_args.pop('arcade_expression', None),
            'valueExpressionTitle' : symbol_args.pop('arcade_title', None),
            'visualVariable' : symbol_args.pop('visual_variable', None),
            'rotationType' : symbol_args.pop('rotation_type', 'arithmetic'),
            'rotationExpression' : symbol_args.pop('rotation_expression', None),
            'normalizationType' : symbol_args.pop('normalization_type', None),
            'normalizationTotal' : symbol_args.pop('normalization_total', None),
            'normalizationField' : symbol_args.pop('normalization_field', None),
            'minValue' : symbol_args.pop('min_value', 0),
            'field' : symbol_args.pop('field'),
            'defaultSymbol' : symbol_args.pop('default_symbol', create_symbol(
                geometry_type=sdf_or_series.geometry_type,
                cmap=cmap)
                                              ),
            'defaultLabel' : symbol_args.pop('default_label', 'Other'),
            'classificationMethod' : symbol_args.pop('method', 'esriClassifyEqualInterval'),
            'classBreakInfos' : [],
            'backgroundFillSymbol' : symbol_args.pop('background_fill_symbol', None)
        }
        minValue = sdf_or_series[renderer['field']].min()
        maxValue = sdf_or_series[renderer['field']].max()
        def pairwise(iterable, fillvalue=999):
            "s -> (s0,s1), (s1,s2), (s2, s3), ..."
            a, b = itertools.tee(iterable)
            next(b, None)
            return itertools.zip_longest(a, b)
        # calculate the class breaks from column data
        cbs = []
        breaks = np.linspace(minValue, maxValue,
                             num=class_count).tolist()
        ss = symbol_args.pop('symbol_style', None)
        st = symbol_args.pop('symbol_type', None)
        for pair in pairwise(breaks, fillvalue=maxValue):

            cbs.append({
                "classBreakInfo": {
                    'classMaxValue' : pair[1],
                    'label' : "%s - %s" % (pair[0], pair[1]),
                    'description' : "%s - %s" % (pair[0], pair[1]),
                    'symbol' : create_symbol(geometry_type=sdf_or_series.geometry_type,
                                             symbol_style=ss,
                                             symbol_type=st,
                                             cmap=cmap,
                                             **symbol_args)
                }
            })
            del cb
        renderer['classBreakInfos'] = cbs
        return renderer
    #elif renderer_type == "p":
    #    renderer = {}
    elif renderer_type == "str":
        renderer = {
            'computeGamma' : symbol_args.pop('compute_gamma', True),
            'dra' : symbol_args.pop('dra', None),
            'gamma' : symbol_args.pop('gamma', None),
            'max' : symbol_args.pop('max_value', None),
            'min' : symbol_args.pop('min_value', None),
            'maxPercent' : symbol_args.pop('max_percent', None),
            'minPercent' : symbol_args.pop('min_percent', None),
            "numberOfStandardDeviations" : symbol_args.pop('std', None),
            'sigmoidStrengthLevel' : symbol_args.pop('sigmoid', None),
            'statistics' : symbol_args.pop('statistics', None),
            'stretchType' : symbol_args.pop('type', 'none'),
            'type' : 'rasterStretch',
            'useGamma' : symbol_args.pop('use_gamme', False)
        }
        return renderer
    elif renderer_type == "t":
        renderer = {
            'type' : 'temporal',
            'latestObservationRenderer' : symbol_args.pop('latest_observation',
                                                          render(
                                                              label="Latest",
                                                              render_type='s',
                                                              cmap=cmap,
                                                              sdf_or_series=sdf_or_series,
                                                              **symbol_args)
                                                          ),
            'observationRenderer' : symbol_args.pop('observation',
                                                    render(
                                                        label="Observation",
                                                        render_type='s',
                                                        cmap=cmap,
                                                        sdf_or_series=sdf_or_series,
                                                        **symbol_args)
                                                    ),
            'trackRenderer' : symbol_args.pop('track',
                                              render(
                                                  label="Track",
                                                  render_type='s',
                                                  cmap=cmap,
                                                  sdf_or_series=sdf_or_series,
                                                  **symbol_args)
                                              )
        }
        return renderer
    return renderer
