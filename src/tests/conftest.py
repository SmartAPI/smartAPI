import os
import sys

dirname = os.path.dirname(__file__)
SRC_PATH = os.path.dirname(dirname)
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

if "TEST_CONF" not in os.environ:
    os.environ["TEST_CONF"] = os.path.join(SRC_PATH, "config.py")
