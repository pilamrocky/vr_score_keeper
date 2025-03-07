import os

if os.environ.get("ENV") == "prod":
    from .prod import *
else:
    from .dev import *
