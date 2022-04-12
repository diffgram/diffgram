from shared.settings import settings
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy_utils.functions import drop_database
from sqlalchemy import create_engine
from shared.database_setup_supporting import *
import alembic.config
import pathlib
import os

parent_path = pathlib.Path().resolve().parent.parent.parent
init_config_path = f"{parent_path}/shared"

os.chdir(init_config_path)
if settings.DIFFGRAM_SYSTEM_MODE != 'testing_e2e':
    raise Exception('Can only set database when mode is: testing_e2e'
                    '')
engine = create_engine(settings.DATABASE_URL)
print(f'Checking DB: {settings.DATABASE_URL}')
if not database_exists(engine.url):
    create_database(engine.url)
    alembic_args = [
        '--raiseerr',
        'upgrade',
        'head',
    ]
    alembic.config.main(argv = alembic_args)
    print('Database created successfully.')
else:
    print(f"Destroying database: {settings.DATABASE_URL}")
    drop_database(settings.DATABASE_URL)
    print(f"Creating DB: {settings.DATABASE_URL}")
    create_database(engine.url)
    alembic_args = [
        '--raiseerr',
        'upgrade',
        'head',
    ]
    alembic.config.main(argv = alembic_args)
    print('Database created successfully.')
