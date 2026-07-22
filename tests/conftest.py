import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["API_KEYS"] = "valid-test-key-12345"
os.environ["PYTHON_ENV"] = "test"
