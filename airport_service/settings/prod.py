from .base import *


DEBUG = False
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS if h.strip()]


RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
if not ALLOWED_HOSTS:
    raise ValueError(
        "Змінна середовища ALLOWED_HOSTS повинна бути встановлена у продакшні."
    )

import dj_database_url

if os.getenv("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(
            default=os.getenv("DATABASE_URL"),
            conn_max_age=600
        )
    }
    # Render or other platforms might already include sslmode in the connection string.
    # We can override or default it to require.
    if os.getenv("POSTGRES_SSLMODE"):
        DATABASES["default"]["OPTIONS"] = {
            "sslmode": os.getenv("POSTGRES_SSLMODE")
        }
    else:
        DATABASES["default"]["OPTIONS"] = {
            "sslmode": "require",
        }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB"),
            "USER": os.getenv("POSTGRES_USER"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
            "HOST": os.getenv("POSTGRES_HOST"),
            "PORT": os.getenv("POSTGRES_DB_PORT", 5432),
            "OPTIONS": {
                "sslmode": "require",
            },
        }
    }

# Захист безпеки
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 рік
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
