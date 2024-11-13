import os
import pathlib
import sys

SRC_PATH = pathlib.Path(__file__).parent.parent

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH.as_posix())

if "TEST_CONF" not in os.environ:
    os.environ["TEST_CONF"] = "config_test.py"
