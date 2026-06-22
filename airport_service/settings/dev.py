from .base import *

import os

DEBUG = os.environ.get("DEBUG", "True") == "True"

if os.environ.get("ALLOWED_HOSTS"):
    ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS").split(",") if h.strip()]
else:
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

INSTALLED_APPS += ["debug_toolbar"]

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")



