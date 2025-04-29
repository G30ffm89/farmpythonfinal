import os
from dotenv import load_dotenv 
from datetime import timedelta

load_dotenv()

class Config(object):
    pass

class ProdConfig(Config):
    SECRET_KEY = os.getenv('S_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('PASSWORD_SALT')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_API_ENABLED = True
    SECURITY_FRESHNESS = timedelta(minutes=30)
    SECURITY_FRESHNESS_GRACE_PERIOD = timedelta(minutes=5)
    #SQLALCHEMY_ENGINE_OPTIONS = True
    SECURITY_REGISTERABLE = True
    SESSION_COOKIE_PERMANENT = False # session exist providing remember me is pressed
    SECURITY_TRACKABLE = True
    SECURITY_EMAIL_SUBJECT_PASSWORD_RESET = "Fruiting Oasis Password Creation Invitation"
    SECURITY_EMAIL_SUBJECT_CONFIRM = "Fruiting Oasis Account Creation"
    SECURITY_RECOVERABLE = True
    SECURITY_REMEMBER_ME_DURATION = timedelta(days=30) #Duration of the Flask-Security rember me option
    REMEMBER_COOKIE_SAMESITE = "strict"
    SESSION_COOKIE_SAMESITE = "strict"
    SECURITY_POST_LOGIN_VIEW = '/'
    SECURITY_POST_REGISTER_VIEW = '/'
    SECURITY_POST_LOGOUT_VIEW  = '/login'
    SECURITY_LOGIN_USER_TEMPLATE = 'security/login_user.html'
    SECURITY_CHANGEABLE = True
    SECURITY_CHANGE_PASSWORD_TEMPLATE = 'security/change_password.html'
    SECURITY_RESET_PASSWORD_TEMPLATE = 'security/reset_password.html'
    SECURITY_REGISTER_USER_TEMPLATE = 'security/register_user.html'
    SECURITY_TWO_FACTOR_VERIFY_CODE_TEMPLATE = 'security/two_factor_verify_code.html'
    SECURITY_TWO_FACTOR_REQUIRED = True
    SECURITY_TWO_FACTOR = True
    SECURITY_TWO_FACTOR_ENABLED_METHODS = ['authenticator']
    SECURITY_TWO_FACTOR_RESCUE_MAIL = os.getenv('RESCUE_MAIL')
    SECURITY_TWO_FACTOR_ALWAYS_VALIDATE = 'False'
    SECURITY_TWO_FACTOR_LOGIN_VALIDITY = "1 week"
    #SECURITY_WAN_ALLOW_AS_MULTI_FACTOR = True
    #SECURITY_WAN_ALLOW_AS_VERIFY = True
    #SECURITY_WEBAUTHN = True
    SECURITY_CONFIRMABLE = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = os.getenv('M_UNAME')
    MAIL_PASSWORD = os.getenv('M_PWD')
    SECURITY_TOTP_SECRETS = {"1": os.getenv('TOTP')}
    SECURITY_TOTP_ISSUER = "Frutiting Oasis Web Application"
    SECURITY_JOIN_USER_ROLES = True
    

class DevConfig(Config):
    DEBUG = True
    SECRET_KEY = os.getenv('S_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('S_PASSWORD_SALT')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #SQLALCHEMY_ENGINE_OPTIONS = True
    SECURITY_REGISTERABLE = True
    SESSION_COOKIE_PERMANENT = False # session exist providing remember me is pressed
    SECURITY_TRACKABLE = True
    SECURITY_EMAIL_SUBJECT_PASSWORD_RESET = "Fruiting Oasis Password Creation Invitation"
    SECURITY_EMAIL_SUBJECT_CONFIRM = "Fruiting Oasis Account Creation"
    SECURITY_RECOVERABLE = True
    SECURITY_REMEMBER_ME_DURATION = timedelta(days=30) #Duration of the Flask-Security rember me option
    REMEMBER_COOKIE_SAMESITE = "strict"
    SESSION_COOKIE_SAMESITE = "strict"
    SECURITY_POST_LOGIN_VIEW = '/'
    SECURITY_POST_REGISTER_VIEW = '/'
    SECURITY_POST_LOGOUT_VIEW  = '/login'
    SECURITY_LOGIN_USER_TEMPLATE = 'security/login_user.html'
    SECURITY_CHANGEABLE = True
    SECURITY_CHANGE_PASSWORD_TEMPLATE = 'security/change_password.html'
    SECURITY_RESET_PASSWORD_TEMPLATE = 'security/reset_password.html'
    SECURITY_REGISTER_USER_TEMPLATE = 'security/register_user.html'
    SECURITY_TWO_FACTOR_VERIFY_CODE_TEMPLATE = 'security/two_factor_verify_code.html'
    SECURITY_TWO_FACTOR_REQUIRED = True
    SECURITY_TWO_FACTOR = True
    SECURITY_TWO_FACTOR_ENABLED_METHODS = ['authenticator']
    SECURITY_TWO_FACTOR_RESCUE_MAIL = os.getenv('RESCUE_MAIL')
    SECURITY_TWO_FACTOR_ALWAYS_VALIDATE = 'False'
    SECURITY_TWO_FACTOR_LOGIN_VALIDITY = "1 week"
    SECURITY_WAN_ALLOW_AS_MULTI_FACTOR = True
    SECURITY_WAN_ALLOW_AS_VERIFY = True
    SECURITY_WEBAUTHN = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = os.getenv('M_UNAME')
    MAIL_PASSWORD = os.getenv('M_PWD')
    SECURITY_TOTP_SECRETS = {"1": os.getenv("TOTP")}
    SECURITY_TOTP_ISSUER = "Fruting Oasis web application"

