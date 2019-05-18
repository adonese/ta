"""
Site-wide settings
"""
import os

if os.getenv("prod"):
    ABSOLUTE_URL = "/pin"
else:
    ABSOLUTE_URL = ""