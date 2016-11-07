# -------------------------------------------------------------------------------
# Name:        dino_precondition_checks.py
# Purpose:     This file checks if pre conditions are met before running the Python tests
#-------------------------------------------------------------------------------
import sys
import os
import configparser

class PreconditionChecks():
    """
    Class with methods that can check if pre-conditions are met before running the tests
    """

    @staticmethod
    def get_OS():
        """
        The API works on all 3 major OS. This method is just to find the platform OS report it.
        Expand this if some components will not work on a particular OS
        :return: string representing the OS
        """
        platform = sys.platform
        return platform

    @staticmethod
    def check_API_import():
        """Check if ArcPy can be imported successfully
        Returns bool - True / False"""
        try:
            import arcgis
        except ImportError:
            print("PreConditionCheck: ArcGIS Python API cannot be imported")
            return False
        else:
            return True

    @staticmethod
    def check_ArcPy_import():
        """Check if ArcPy can be imported successfully
        Returns bool - True / False"""
        try:
            import arcpy
        except ImportError:
            return False
        else:
            return True

    @staticmethod
    def check_Pro_installed():
        """Check if ArcGISPro is installed
        Returns bool - True / False"""
        try:
            import arcpy
            installInfo = arcpy.GetInstallInfo()
            if installInfo.get('ProductName') == "ArcGISPro":
                return True
            else:
                print("Installed local GIS: " + installInfo.get('ProductName'))
                return False
        except ImportError:
            return False

    @staticmethod
    def check_Python_version():
        """Checks if Python version is 3.4 and above
        Returns bool"""
        if ((sys.version_info.major >= 3) & (sys.version_info.minor >= 4)):
            print("PreConditionCheck: Python version: " + sys.version)
            return True
        else:
            print("PreConditionCheck: Incompatible Python Version: " + sys.version)
            return False

    @staticmethod
    def check_Pro_is_running():
        """To expand in future. This is to find if Pro is running for cases where the API uses Pro's active portal and
        active token"""
        pass

    @staticmethod
    def can_ping_portal(url):
        """
        This is to check if portal is alive and can be reached
        :return: bool
        """
        import urllib
        try:
            resp = urllib.request.urlopen(url)
            if resp.status == 200:
                return True
            else:
                return False
        except urllib.error.URLError:
            return False
