import os
import sys

# Add the src directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)
# Also add the project root to handle imports from tests directory
if project_root not in sys.path:
    sys.path.insert(0, project_root)
