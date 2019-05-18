"""
Site-wide settings
"""
import os
import jinja2

if os.getenv("prod"):
    ABSOLUTE_URL = "/pin"
else:
    ABSOLUTE_URL = ""

