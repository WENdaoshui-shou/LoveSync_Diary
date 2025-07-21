import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-4-d)(2%**9snt1r8m&z3)ds955jsptqd+##9=95us9-xb8ur##'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'App.apps.AppConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'DjangoPro1.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'DjangoPro1.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lovesync_diary',  # 数据库名字
        'USER': 'root',  # 用户名
        'PASSWORD': '1028',  # 密码
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",  # Redis地址和数据库编号
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'  # 静态文件的 URL 前缀
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # 全局静态文件目录（可选）
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # 生产环境收集静态文件的目录

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'  # 指定登录页面的URL名称
LOGIN_REDIRECT_URL = 'community'  # 登录成功后重定向的页面
LOGOUT_REDIRECT_URL = 'login'  # 登出后重定向的页面

SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # 关闭浏览器后失效

AUTH_USER_MODEL = 'App.User'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 上传文件大小
DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400  # 25MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 26214400  # 25MB

# 验证码过期时间（秒）
VERIFY_CODE_EXPIRE = 60

# 实时共同编辑：
# 通过 WebSocket 实现实时通信
# 使用版本控制机制处理并发编辑
# 模拟 OT 操作的应用和同步
# 埋点服务：
# 设计行为日志模型
# 实现 API 接口接收埋点数据
# 在前端关键操作处触发埋点
# JWT 双令牌验证：
# 自定义 JWT 生成和验证工具
# 实现访问令牌和刷新令牌的分离
# 处理令牌过期和刷新逻辑
# 协同过滤推荐与实时排行榜：
# 使用 Redis 存储话题热度和相似关系
# 实现基于用户行为的简单推荐算法
# 实时更新和展示热门话题排行榜