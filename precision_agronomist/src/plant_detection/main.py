# This file is required for CrewAI deployment
# It redirects to the actual main implementation

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'precision_agronomist'))

from precision_agronomist.main import run, train, test, replay

# Export the functions for CrewAI deployment
__all__ = ['run', 'train', 'test', 'replay']
