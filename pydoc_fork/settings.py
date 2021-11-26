"""
Configuration options that could be used by anything.
"""
import os
import sys

PREFER_INTERNET_DOCUMENTATION = True
DOCUMENT_INTERNALS = False
OUTPUT_FOLDER = ""

PYTHONDOCS = os.environ.get(
    "PYTHONDOCS", "https://docs.python.org/%d.%d/library" % sys.version_info[:2]
)
