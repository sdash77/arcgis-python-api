arcgis.raster.realitymapping module
===================================

.. automodule:: arcgis.raster.realitymapping


is_supported
------------
.. autofunction:: arcgis.raster.realitymapping.is_supported

Project
-------
.. autoclass:: arcgis.raster.realitymapping.Project
    :inherited-members:
    :members:
    :undoc-members:
    :show-inheritance:

Mission
-------
.. autoclass:: arcgis.raster._realitymapping_mission.Mission
    :inherited-members:
    :members:
    :undoc-members:
    :show-inheritance:


.. _default_settings:

Default settings
^^^^^^^^^^^^^^^^

Satellite scenario:

.. code-block:: python

    {'rasterType': 'Satellite',
    'adjustSettings': {'maxResidual': 5,
    'maskPolygons': '',
    'pointDensity': 'MEDIUM',
    'adjustTiePoints': False,
    'pointSimilarity': 'MEDIUM',
    'locationAccuracy': 'MEDIUM',
    'generateTiePoints': True,
    'pointDistribution': 'RANDOM',
    'transformationType': 'RPC'},
    'processingSettings': {'dsm': {'dsm': {'format': 'TIFF',
    'outputType': 'TILED',
    'resampling': 'BILINEAR',
    'compression': 'NONE',
    'noDataValue': 'NaN',
    'lERCMaxError': 0,
    'pyramidSettings': 'PYRAMIDS -1 BILINEAR DEFAULT 75 NO_SKIP',
    'compressionQuality': 75},
    'interpolation': {}},
    'dtm': {'dtm': {'mask': '',
    'extent': '',
    'format': 'CRF',
    'fillDEM': '',
    'cellsize': 'NaN',
    'lowNoise': 0.25,
    'highNoise': 100,
    'compression': 'NONE',
    'reuseGround': False,
    'lERCMaxError': 0,
    'reuseLowNoise': False,
    'cellsizeFactor': 5,
    'reuseHighNoise': False,
    'pyramidSettings': 'PYRAMIDS -1 BILINEAR DEFAULT 75 NO_SKIP',
    'smoothingMethod': 'GAUSS5x5',
    'classifyLowNoise': True,
    'classifyHighNoise': True,
    'useCellsizeFactor': True,
    'compressionQuality': 75,
    'interpolationMethod': 'IDW',
    'groundDetectionMethod': 'Standard'},
   'interpolation': {'method': 'IDW'}},
    'ortho': {},
    '3dMesh': {'format': 'SLPK', 'textureFormat': 'JPG & DDS'},
    'dsmMesh': {'format': 'SLPK', 'textureFormat': 'JPG & DDS'},
    'Trueortho': {'format': 'TIFF',
    'outputType': 'TILED',
    'resampling': 'BILINEAR',
    'compression': 'NONE',
    'noDataValue': 'NaN',
    'lERCMaxError': 0,
    'pyramidSettings': 'PYRAMIDS -1 BILINEAR DEFAULT 75 NO_SKIP',
    'compressionQuality': 75},
    'generalReconSettings': {'quality': 'ULTRA',
    'cellsize': 'NaN',
    'autoCellsize': True,
    'cellsizeFactor': 1,
    'useCellsizeFactor': True},
    'advancedReconSettings': {'productBoundary': '',
    'processingFolder': '',
    'waterbodyFeatures': '',
    'correctionFeatures': '',
    'exportMapWithStereoModelCountOfFinalPoint': False,
    'exportDistanceMapToNextNonInterpolatedPixels': False,
    'exportBinaryMaskImageForNonInterpolatedPixels': False}}}

Drone scenario:

.. code-block:: python

    {'rasterType': 'UAV/UAS',
    'adjustSettings': {'k': True,
    'p': True,
    'estimateOPK': False,
    'focalLength': True,
    'maxResidual': 5,
    'maskPolygons': '',
    'principalPoint': True,
    'rollingShutter': False,
    'adjustTiePoints': False,
    'locationAccuracy': 'HIGH',
    'cameraCalibration': True,
    'processAsRigCamera': False,
    'transformationType': 'Frame',
    'initPointResolution': 8,
    'computeImagePosteriorStd': True,
    'computeSolutionPointPosteriorStd': False,
    'fixImageLocationForHighAccuracyGPS': False},
    'processingSettings': {'dsm': {'dsm': {'format': 'TIFF',
    'outputType': 'TILED',
    'resampling': 'BILINEAR',
    'compression': 'NONE',
    'noDataValue': 'NaN',
    'lERCMaxError': 0,
    'pyramidSettings': 'PYRAMIDS -1 BILINEAR DEFAULT 75 NO_SKIP',
    'compressionQuality': 75},
    'interpolation': {}},
    'dtm': {'dtm': {'mask': '',
    'extent': '',
    'format': 'CRF',
    'fillDEM': '',
    'cellsize': 'NaN',
    'lowNoise': 0.25,
    'highNoise': 100,
    'compression': 'NONE',
    'reuseGround': False,
    'lERCMaxError': 0,
    'reuseLowNoise': False,
    'cellsizeFactor': 5,
    'reuseHighNoise': False,
    'pyramidSettings': 'PYRAMIDS -1 BILINEAR DEFAULT 75 NO_SKIP',
    'smoothingMethod': 'GAUSS5x5',
    'classifyLowNoise': True,
    'classifyHighNoise': True,
    'useCellsizeFactor': True,
    'compressionQuality': 75,
    'interpolationMethod': 'IDW',
    'groundDetectionMethod': 'Standard'},
    'interpolation': {'method': 'IDW'}},
    'ortho': {},
    '3dMesh': {'format': 'SLPK', 'textureFormat': 'JPG & DDS'},
    'dsmMesh': {'format': 'SLPK', 'textureFormat': 'JPG & DDS'},
    'Trueortho': {'format': 'TIFF',
    'outputType': 'TILED',
    'resampling': 'BILINEAR',
    'compression': 'NONE',
    'noDataValue': 'NaN',
    'lERCMaxError': 0,
    'pyramidSettings': 'PYRAMIDS -1 BILINEAR DEFAULT 75 NO_SKIP',
    'compressionQuality': 75},
    'generalReconSettings': {'quality': 'HIGH',
    'cellsize': 'NaN',
    'autoCellsize': True,
    'cellsizeFactor': 1,
    'useCellsizeFactor': True},
    'advancedReconSettings': {'productBoundary': '',
    'processingFolder': '',
    'waterbodyFeatures': '',
    'correctionFeatures': '',
    'exportMapWithStereoModelCountOfFinalPoint': False,
    'exportDistanceMapToNextNonInterpolatedPixels': False,
    'exportBinaryMaskImageForNonInterpolatedPixels': False}}}
