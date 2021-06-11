from shared.settings import settings
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy_utils.functions import drop_database
from sqlalchemy import create_engine
import alembic.config
import pathlib
import os

parent_path = pathlib.Path(__file__).parent.parent.parent.absolute()
init_config_path = '{}/shared'.format(parent_path)

os.chdir(init_config_path)
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
        create_database(engine.url)
        alembic_args = [
            '--raiseerr',
            'upgrade',
            'head',
        ]
        alembic.config.main(argv = alembic_args)
        print('Database created successfully.')
    engine.dispose()


def pytest_unconfigure(config):
    if not config.getoption('--keep-db'):
        print('Destroying database: {}'.format(settings.DATABASE_URL))
        drop_database(settings.DATABASE_URL)

