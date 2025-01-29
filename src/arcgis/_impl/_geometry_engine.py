import os


class GeometryEngine:
    """Manages detection and selection of a spatial geometry engine."""

    _available_engines = {
        "arcpy": False,
        "shapely": False,
        "gdal": False,
        "fiona": False,
    }

    def __init__(self):
        """Initialize and select an engine."""
        self._detect_available_engines()
        self.engine = self._select_engine()  # Store the selected engine
        self.has_arcpy = self._available_engines["arcpy"]
        self.has_pyshp = self._available_engines["shapely"]
        self.has_gdal = self._available_engines["gdal"]
        self.has_fiona = self._available_engines["fiona"]

    def _detect_available_engines(self):
        """Check for installed spatial libraries."""
        try:
            import arcpy

            self._available_engines["arcpy"] = True
        except ImportError:
            pass

        try:
            import shapely

            self._available_engines["shapely"] = True
        except ImportError:
            pass

        try:
            import osgeo

            self._available_engines["gdal"] = True
        except ImportError:
            pass

        try:
            import fiona

            self._available_engines["fiona"] = True
        except ImportError:
            pass

    def _select_engine(self):
        """Select the best available engine, prioritizing user preference."""
        preferred_engine = os.getenv("GEOMETRY_ENGINE", "").lower()

        if (
            preferred_engine in self._available_engines
            and self._available_engines[preferred_engine]
        ):
            return preferred_engine  # Use user-specified engine if available

        # Default priority order: arcpy > gdal > shapely > fiona
        for engine in ["arcpy", "gdal", "shapely", "fiona"]:
            if self._available_engines[engine]:
                return engine

        raise ImportError(
            "No valid spatial library found. Install `arcpy`, `shapely`, `gdal`, or `fiona`."
        )


# Create a global instance so all modules can import it
ge = GeometryEngine()
SELECTED_ENGINE = ge.engine
HAS_ARCPY = ge.has_arcpy
HAS_PYSHP = ge.has_pyshp
HAS_GDAL = ge.has_gdal
HAS_FIONA = ge.has_fiona
