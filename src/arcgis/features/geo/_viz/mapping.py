"""
Mapping Holds the Plot function for creating a FeatureCollection JSON plus the render options
"""
import json
from typing import Optional, Union
import pandas as pd

from arcgiswidgets.widgets.map_widget import Map

# from arcgiswidgets._dataclasses.symbols import (
#     create_picture_fill_symbol,
#     create_picture_marker_symbol,
#     create_simple_fill_symbol,
#     create_simple_line_symbol,
#     create_simple_marker_symbol,
#     create_text_symbol
# )
# from arcgiswidgets._dataclasses.renderers import (
#     create_simple,
#     create_visual_variables,
# )


def plot(
    df,
    map_widget: Optional[Map] = None,
    name: Optional[str] = None,
    renderer_type: Optional[str] = None,
    symbol_type: Optional[str] = None,
    symbol_style: Optional[str] = None,
    col: Optional[Union[str, list]] = None,
    colors: Optional[Union[str, list, object]] = "jet",
    alpha: float = 1,
    **kwargs,
):
    """

    Plot draws the data on a web map. The user can describe in simple terms how to
    renderer spatial data using symbol.  To make the process simplier a palette
    for which colors are drawn from can be used instead of explicit colors.


    ======================  =========================================================
    **Explicit Argument**   **Description**
    ----------------------  ---------------------------------------------------------
    df                      Required Spatially Enabled DataFrame or GeoSeries. This is the data
                            to map.
    ----------------------  ---------------------------------------------------------
    map_widget              Optional WebMap object. This is the map to display the
                            data on.
    ----------------------  ---------------------------------------------------------
    name                    Optional string. The name to assign as a title of the map widget.
    ======================  =========================================================

    The kwargs parameter accepts all parameters of the create_symbol method and the
    create_renderer method.


    """
    renderer = kwargs.pop("renderer", None)

    if not hasattr(df, "spatial") and not hasattr(df, "geom"):
        raise ValueError("DataFrame or Series must be spatially enabled.")

    if renderer_type is None and renderer is None and df.spatial.renderer:
        renderer = json.loads(df.spatial.renderer.json)

    if isinstance(df, pd.Series) and df.dtype.name == "geometry":
        fid = df.index.tolist()
        sdf = pd.DataFrame(data=fid, columns=["OID"])
        sdf["SHAPE"] = df
        return plot(
            df=sdf,
            map_widget=map_widget,
            name=name,
            renderer_type=renderer_type,
            symbol_type=symbol_type,
            symbol_style=symbol_style,
            col=col,
            colors=colors,
            alpha=alpha,
            **kwargs,
        )
    r = None
    if isinstance(col, str):
        col = [col]
    map_exists = True
    if symbol_type is None:
        symbol_type = "simple"
    if name is None:
        import uuid

        name = uuid.uuid4().hex[:7]
    if map_widget is None:
        map_exists = False
        map_widget = Map()
    import string

    trantab = str.maketrans(string.punctuation, "_" * len(string.punctuation))
    col_new = [col.translate(trantab) for col in df.columns]
    col_old = df.columns.tolist()
    df.columns = col_new
    fc = df.spatial.to_feature_collection(name=name)
    df.columns = col_old
    geometry_type = [el for el in df.spatial.geometry_type if el is not None]
    map_widget.add_layer(fc)
    return map_widget
