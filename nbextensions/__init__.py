import sys
if sys.version_info.major != 3:
    # at present we only support python3 because we want to rely on FStrings and other goodness
    raise ValueError('We only support Python 3; recommended Python 3.6')

from .setup import __version__
from .magics import *
from .keyrings import *
