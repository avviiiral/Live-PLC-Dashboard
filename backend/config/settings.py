import os
from pathlib import Path
BASE_DIR=Path(__file__).resolve().parent.parent
ROOT_DIR=BASE_DIR.parent
SECRET_KEY=os.getenv('DJANGO_SECRET_KEY','development-only-change-me')
DEBUG=os.getenv('DJANGO_DEBUG','true').lower() in {'1','true','yes'}
ALLOWED_HOSTS=[x.strip() for x in os.getenv('DJANGO_ALLOWED_HOSTS','localhost,127.0.0.1').split(',') if x.strip()]
TIME_ZONE=os.getenv('TIME_ZONE','Asia/Kolkata');USE_TZ=True;LANGUAGE_CODE='en-us';DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
INSTALLED_APPS=['daphne','django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','rest_framework','corsheaders','channels','drf_spectacular','core']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','corsheaders.middleware.CorsMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF='config.urls';ASGI_APPLICATION='config.asgi.application';WSGI_APPLICATION='config.wsgi.application'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
CHANNEL_LAYERS={'default':{'BACKEND':'channels.layers.InMemoryChannelLayer'}}
CORS_ALLOWED_ORIGINS=[x.strip() for x in os.getenv('DJANGO_CORS_ALLOWED_ORIGINS','http://localhost:4200').split(',') if x.strip()]
REST_FRAMEWORK={'DEFAULT_AUTHENTICATION_CLASSES':['rest_framework.authentication.SessionAuthentication','rest_framework.authentication.BasicAuthentication'],'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.IsAuthenticatedOrReadOnly'],'DEFAULT_SCHEMA_CLASS':'drf_spectacular.openapi.AutoSchema','DEFAULT_PAGINATION_CLASS':'rest_framework.pagination.PageNumberPagination','PAGE_SIZE':50}
SPECTACULAR_SETTINGS={'TITLE':'Live PLC Dashboard API','VERSION':'1.0.0'}
engine=os.getenv('DB_ENGINE','sqlite').lower()
if engine=='sqlite': DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':ROOT_DIR/os.getenv('SQLITE_PATH','backend/db.sqlite3'),'OPTIONS':{'timeout':20}}}
elif engine=='postgresql': DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':os.getenv('POSTGRES_DB','live_plc'),'USER':os.getenv('POSTGRES_USER','live_plc'),'PASSWORD':os.getenv('POSTGRES_PASSWORD',''),'HOST':os.getenv('POSTGRES_HOST','127.0.0.1'),'PORT':os.getenv('POSTGRES_PORT','5432'),'CONN_MAX_AGE':60}}
else: raise RuntimeError('DB_ENGINE must be sqlite or postgresql')
STATIC_URL='static/';STATIC_ROOT=BASE_DIR/'staticfiles';SECURE_CONTENT_TYPE_NOSNIFF=True;SESSION_COOKIE_HTTPONLY=True
