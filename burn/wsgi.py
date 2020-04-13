from burn.server import app as application
import sys
import os
import logging
import sys

# To fix error logs not showing in apache.
logging.basicConfig(stream=sys.stderr)
