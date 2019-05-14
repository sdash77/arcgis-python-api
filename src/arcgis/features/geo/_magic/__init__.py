"""
The Spatially Enabled DataFrames' Magic Method
"""
from traitlets.config.application import Application
from IPython.core import magic_arguments
from IPython.core.magic import Magics, magics_class, line_magic
from IPython.testing.skipdoctest import skip_doctest

#-----------------------------------------------------------------------------
# Magic implementation classes
#-----------------------------------------------------------------------------


@magics_class
class ArcGISMagics(Magics):
    """Magics related to the Spatially Enabled DataFrame"""

    @skip_doctest
    @line_magic
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('-h', '--help', action='store_true',
                              help='Shows a help message')
    def spatially_enable(self, line=''):
        """
        Sets up the Pandas DataFrame to be spatially enabled.

        This function lets you activate the `spatial` and `geom`
        namespaces without having to import anything into the interactive
        namespace.


        Example
        --------
        To enable the spatially enabled dataframe namespace::

            In [1]: %spatiallyenabled
            In [2]: import pandas as pd
            In [3]: sdf = pd.DataFrame.spatial.from_featureclass("<path>")

        """
        args = magic_arguments.parse_argstring(self.spatially_enable, line)
        if args.help:
            print("Loads the `spatial` namspaces into Pandas' `DataFrame` and `geom` into `Series`")
        else:
            import pandas as pd
            from arcgis.features import GeoAccessor, GeoSeriesAccessor