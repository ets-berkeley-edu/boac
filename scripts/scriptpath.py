# Boilerplate allowing scripts in the /scripts directory to find the boac module.
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from boac.lib import scriptify
