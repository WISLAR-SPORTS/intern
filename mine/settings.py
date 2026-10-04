

import os
import dj_database_url

from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent



# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-e^q33&&$^ncwvzzfz34e!#dyhjq1pwdttetfma29*8ojco5&-+'
#SECRET_KEY = os.environ.get("SECRET_KEY")
import os




# ...

BREVO_API_KEY = os.getenv("BREVO_API_KEY")

BREVO_SENDER_EMAIL = os.getenv(
    "BREVO_SENDER_EMAIL"
)

BREVO_SENDER_NAME = os.getenv(
    "BREVO_SENDER_NAME",
    "InternLink Ug",
)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL")
BREVO_SENDER_NAME = os.getenv("BREVO_SENDER_NAME")
 
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL",
    "https://openrouter.ai/api/v1",
)
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openrouter/free",
)
TURNSTILE_SITE_KEY = os.getenv("TURNSTILE_SITE_KEY", "")
TURNSTILE_SECRET_KEY = os.getenv("TURNSTILE_SECRET_KEY", "")
# ==========================================
# LEGAL DOCUMENT VERSIONS
# ==========================================

TERMS_VERSION = "1.0"
PRIVACY_VERSION = "1.0"


import cloudinary
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
)



# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = True

ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = [
      "http://10.58.226.248:8000",
    "https://spec-lenders-digital-extensions.trycloudflare.com",
]

AUTH_USER_MODEL = "accounts.User"


# Application definition
from datetime import timedelta


REST_FRAMEWORK = {

    "DEFAULT_AUTHENTICATION_CLASSES": (

        "rest_framework_simplejwt.authentication.JWTAuthentication",

    )

}


SIMPLE_JWT = {

    "ACCESS_TOKEN_LIFETIME":
        timedelta(minutes=60),

}
INSTALLED_APPS = [
     "jazzmin",

    "accounts",
    "students",
    "companies",
   
      "dashboard",
      "ai_assistant",

     "rest_framework",
    "corsheaders",
     'cloudinary',
   
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "internships.apps.InternshipConfig",

]

MIDDLEWARE = [
     "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
   # "accounts.middleware.ConsentMiddleware",
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
     "whitenoise.middleware.WhiteNoiseMiddleware",
   
    
]
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
ROOT_URLCONF = 'mine.urls'

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
          "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "dashboard.context_processors.university_metrics",
                "accounts.context_processors.landing_settings",
                "students.context_processors.notification_count",


            ],
        },
    },
    
]
WSGI_APPLICATION = 'mine.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
} """


DATABASES = {
    "default": dj_database_url.config(
        conn_max_age=600
    )
} 


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
JAZZMIN_SETTINGS = {
    "site_title": "Student System Admin",
    "site_header": "Student System",
    "site_brand": "Student System",

    "welcome_sign": "Welcome to the Student System",

    "show_sidebar": True,
    "navigation_expanded": True,

    "topmenu_links": [
        {
            "name": "University Dashboard",
            "url": "/students/university/",
            "permissions": [
                "accounts.view_university_dashboard",
            ],
        },
        {
            "name": "Company Dashboard",
            "url": "/companies/dashboard/",
            "permissions": [
                "accounts.view_company_dashboard",
            ],
        },
    ],

    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",

        "students.Student": "fas fa-user-graduate",
        "students.Application": "fas fa-file-alt",
    },

    "custom_css": "admin/css/custom_admin.css",
   
}


JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,

    "brand_colour": "primary",
    "accent": "primary",

    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,

    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,

    "theme": "default",
}


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True
LOGIN_REDIRECT_URL = "/internships/company-dashboard/"



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

# Static files

STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static"
]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
LOGIN_URL = "/login/"
LOGOUT_REDIRECT_URL = "/login/"
