from shared.settings import settings
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy_utils.functions import drop_database
from sqlalchemy import create_engine
from shared.database_setup_supporting import *

if settings.DIFFGRAM_SYSTEM_MODE != 'testing':
    raise Exception('DIFFGRAM_SYSTEM_MODE must be in "testing" mode to perform any kind of test')


def pytest_addoption(parser):
    parser.addoption(
        "--keep-db", action="store_true", default=False, help="Don't destroy Database when finishing tests."
    )


def pytest_configure(config):
    engine = create_engine(settings.DATABASE_URL)
    print('Checking DB: {}'.format(settings.DATABASE_URL))
    if not database_exists(engine.url):
        print('Creating DB: {}'.format(settings.DATABASE_URL))
        from shared.database.core import Base
        create_database(engine.url)
        Base.metadata.create_all(engine)
        print('Database created successfully.')
    engine.dispose()


def pytest_unconfigure(config):
    if not config.getoption('--keep-db'):
        print('Destroying database: {}'.format(settings.DATABASE_URL))
        drop_database(settings.DATABASE_URL)

