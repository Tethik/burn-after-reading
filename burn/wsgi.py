import sys
import os
import logging, sys

# To fix error logs not showing in apache.
logging.basicConfig(stream=sys.stderr)
from burn.server import app as application
