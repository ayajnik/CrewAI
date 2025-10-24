# This file is required for CrewAI deployment
# It redirects to the actual crew implementation

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'precision_agronomist'))

from precision_agronomist.crew import PrecisionAgronomist

# Export the crew for CrewAI deployment
__all__ = ['PrecisionAgronomist']
