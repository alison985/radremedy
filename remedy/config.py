"""
config.py

Contains configuration information used throughout the application.
"""
import os

_basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig(object):
    """
    The base configuration used by both development
    and production configurations.
    """

    """
    Indicates if debugging is enabled for the application.
    """
    DEBUG = True

    """
    The URI of the database.
    """
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'rad/rad.db')

    """
    The path to the directory containing database migrations.
    """
    MIGRATIONS_DIR = './remedy/rad/migrations'

    """
    The base URL to the website.
    """
    BASE_URL = 'radremedy.org'

    """
    The username of the account used to send email.

    Retrieved through the RAD_EMAIL_USERNAME environment variable.
    """
    EMAIL_USERNAME = str(os.environ.get('RAD_EMAIL_USERNAME'))

    """
    The full address of the account used to send email,
    and to which error reports will be submitted.

    Retrieved through the RAD_EMAIL_ADDRESS environment variable.
    """
    EMAIL_ADDRESS = str(os.environ.get('RAD_EMAIL_ADDRESS'))

    """
    The password of the account used to send email.

    Retrieved through the RAD_EMAIL_PASSWORD environment variable.
    """
    EMAIL_PASSWORD = str(os.environ.get('RAD_EMAIL_PASSWORD'))

    """
    The address of the server used to send email.
    A port can be included.

    Retrieved through the RAD_EMAIL_SERVER environment variable.
    """
    EMAIL_SERVER = str(os.environ.get('RAD_EMAIL_SERVER'))


class DevelopmentConfig(BaseConfig):
    """
    The configuration used for development environments.
    """
    BASE_URL = 'localhost:5000'


class ProductionConfig(BaseConfig):
    """
    The configuration used for the production environment.
    """
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'rad/rad.db')
