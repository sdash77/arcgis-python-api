import sys
import os
#suds requires the contaning directory to be in sys.path for it to work with package imports
sys.path.append(os.path.dirname(__file__))
#from .shared_utils import *
del sys, os
#import compare   #compare is part of pyunit. 
# Its big, robust and uses arcpy. But today it isn't needed.

