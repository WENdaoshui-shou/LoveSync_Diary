import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-4-d)(2%**9snt1r8m&z3)ds955jsptqd+##9=95us9-xb8ur##'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    '*'
]

CSRF_TRUSTED_ORIGINS = [
    "https://6a10c670.r7.cpolar.top",
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 第三方应用
    'rest_framework',
    'corsheaders',
    # 自定义应用
    'core',
    'moment',
    'couple',
    'note',
    'photo',
    'mall',
    'collab',
    'game',
    'vip',
    'message',
    'user',
    'articles',
    'history',  # 添加历史应用
    'sys_community',  # 社区活动管理应用
    # 其他应用
    'channels',
    'AI',
]

# 使用自定义用户模型
AUTH_USER_MODEL = 'core.User'

# CORS配置
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Django REST Framework配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# JWT配置
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': 'your-secret-key',
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# 通道层配置（使用Redis）
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}


# settings.py 中的日志配置示例
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
            'stream': 'ext://sys.stdout',
        },
    },
    'formatters': {
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
            'log_colors': {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            'datefmt': '%Y-%m-%d %H:%M:%S',  # 统一时间格式
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,  # 关键修改：禁止日志向上传播
        },
        # 处理django.server的日志（避免重复输出请求日志）
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'vip.middleware.VIPStatusCheckMiddleware', 
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 消息存储配置，使用SessionStorage确保消息在渲染后被清除
# 使用Session存储消息，更稳定且无4KB限制
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

ROOT_URLCONF = 'LoveSync.urls'

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
WSGI_APPLICATION = 'LoveSync.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lovesync_diary',
        'USER': 'root',
        'PASSWORD': '1028', 
        'HOST': 'localhost', 
        'PORT': '3306',  
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# Redis连接配置
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')

# 缓存数据库配置
REDIS_DB_DEFAULT = os.getenv('REDIS_DB_DEFAULT', '0')
REDIS_DB_USER_SESSIONS = os.getenv('REDIS_DB_USER_SESSIONS', '0')  # 用户会话缓存数据库
REDIS_DB_MATSER = os.getenv('REDIS_DB_matser', '1')         # 用户数据社区等主要模块的数据库
REDIS_DB_MALL_CACHE = os.getenv('REDIS_DB_MALL_CACHE', '2')     # 商城的缓存数据库（所有商城相关缓存）

# 商城相关缓存使用商城缓存数据库
REDIS_DB_HOT_PRODUCTS = os.getenv('REDIS_DB_HOT_PRODUCTS', REDIS_DB_MALL_CACHE)   # 热卖商品缓存数据库
REDIS_DB_PRODUCT_CACHE = os.getenv('REDIS_DB_PRODUCT_CACHE', REDIS_DB_MALL_CACHE)  # 商品详情缓存数据库

# 缓存配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_DEFAULT}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "hot_products": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_HOT_PRODUCTS}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "user_sessions": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_USER_SESSIONS}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "mall_cache": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_MALL_CACHE}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "product_cache": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_PRODUCT_CACHE}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "master_cache": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB_MATSER}",
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

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# 配置 ASGI 应用
ASGI_APPLICATION = 'LoveSync.asgi.application'

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # 全局静态文件目录
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # 生产环境收集静态文件的目录

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'  # 指定登录页面的URL名称
LOGIN_REDIRECT_URL = 'community'  # 登录成功后重定向的页面
LOGOUT_REDIRECT_URL = 'login'  # 登出后重定向的页面

# SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # 关闭浏览器后失效 - 注释掉以支持"记住我"功能

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
# 大模型API配置




# 会话配置
# 使用Redis存储session，提高性能
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'user_sessions'  # 使用用户会话缓存后端
SESSION_COOKIE_AGE = 3600 * 24 * 7  # 会话有效期7天，与"记住我"功能对应
SESSION_COOKIE_NAME = 'lovesync_session'  # 自定义会话cookie名称
SESSION_COOKIE_SECURE = False  # 开发环境使用HTTP，生产环境应设置为True
SESSION_COOKIE_HTTPONLY = True  # 防止JavaScript访问cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # 防止CSRF攻击，同时确保消息在重定向过程中不会丢失

# 阿里云 OSS 存储配置
if not DEBUG:  # 仅在生产环境使用 OSS
    DEFAULT_FILE_STORAGE = 'core.storage.AliyunOSSStorage'
    STATICFILES_STORAGE = 'core.storage.AliyunOSSStorage'
    
    # OSS URL 配置
    ALIYUN_OSS_BUCKET_NAME = os.environ.get('ALIYUN_OSS_BUCKET_NAME', 'wendaoshuishou')
    ALIYUN_OSS_ENDPOINT = os.environ.get('ALIYUN_OSS_ENDPOINT', 'oss-cn-chengdu.aliyuncs.com')
    
    # 使用 OSS 域名作为媒体文件和静态文件的基础 URL
    MEDIA_URL = f'https://{ALIYUN_OSS_BUCKET_NAME}.{ALIYUN_OSS_ENDPOINT}/'
    STATIC_URL = f'https://{ALIYUN_OSS_BUCKET_NAME}.{ALIYUN_OSS_ENDPOINT}/'