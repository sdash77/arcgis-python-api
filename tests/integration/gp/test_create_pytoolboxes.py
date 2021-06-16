"""import unittest

from arcgis.geoprocessing._tool import create_toolbox
import arcpy, os
from arcgis.features import SpatialDataFrame


def clip(fc:SpatialDataFrame, fc2:SpatialDataFrame) -> SpatialDataFrame:
    return arcpy.Clip_analysis(fc, fc2, out_feature_class=os.path.join(arcpy.env.scratchGDB, "clipper"))

def add(x:float, y:float=15) -> float:
    return x+y

def simpleinterest(principle:float,time:float=30,rate:float=3.6,
                   name:str="", boolean:bool=False ) -> float:
""" """calculates simple interest""" """
    return (principle*time*rate)/100

def failmethod(x,y):
    return x+y

class CreatePYTBX(unittest.TestCase):
    def test_non_arcpy(self):
""" """creates a non-arcpy based pytbx""" """"
        pyt, xml = create_toolbox(func=add, toolbox="AdditionToolbox")
        self.assertTrue(os.path.isfile(pyt))
        self.assertTrue(os.path.isfile(xml))
    def test_arcpy(self):
""" """creates a pytbx with arcpy inputs""" """
        pyt, xml = create_toolbox(func=clip)
        self.assertTrue(os.path.isfile(pyt))
        self.assertTrue(os.path.isfile(xml))
    def test_lots_of_inputs(self):
""" """creates a pytbx with lots of inputs""" """
        pyt, xml = create_toolbox(func=simpleinterest)
        self.assertTrue(os.path.isfile(pyt))
        self.assertTrue(os.path.isfile(xml))
    def test_failing(self):
""" """tests that error is raised when annotations are not provided""" """"
        self.assertRaises(ValueError, create_toolbox, **{"func" : failmethod})
#--------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
"""
