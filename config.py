import os
 

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
    S3_KEY = os.environ.get("S3_ACCESS_KEY")
    S3_SECRET = os.environ.get("S3_SECRET_ACCESS_KEY")
    S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)
    BT_ENVIRONMENT=os.environ.get('BT_ENVIRONMENT')
    BT_MERCHANT_ID=os.environ.get('BT_MERCHANT_ID')
    BT_PUBLIC_KEY=os.environ.get('BT_PUBLIC_KEY')
    BT_PRIVATE_KEY=os.environ.get('BT_PRIVATE_KEY')
    G_CLIENT_ID=os.environ.get('G_CLIENT_ID')
    G_CLIENT_SECRET=os.environ.get('G_CLIENT_SECRET')
    MAIL_DOMAIN=os.environ.get('MAILGUN_DOMAIN')
    MAIL_KEY=os.environ['MAILGUN_API_KEY']
    JWT_ACCESS_TOKEN_EXPIRES= False

class ProductionConfig(Config):
    DEBUG = False
    ASSET_DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = False
    DEBUG = False
    ASSET_DEBUG = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    ASSET_DEBUG = False


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    ASSET_DEBUG = True
