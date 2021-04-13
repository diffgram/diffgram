from shared.settings import settings
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy_utils.functions import drop_database
from sqlalchemy import create_engine
from shared.database_setup_supporting import *

if settings.DIFFGRAM_SYSTEM_MODE != 'testing_e2e':
    raise Exception('Can only set database when mode is: testing_e2e'
                    '')
engine = create_engine(settings.DATABASE_URL)
print('Checking DB: {}'.format(settings.DATABASE_URL))
if not database_exists(engine.url):
    print('Creating DB: {}'.format(settings.DATABASE_URL))
    from shared.database.core import Base

    create_database(engine.url)
    Base.metadata.create_all(engine)
    print('Database created successfully.')
else:
    print('Destroying database: {}'.format(settings.DATABASE_URL))
    drop_database(settings.DATABASE_URL)
    print('Creating DB: {}'.format(settings.DATABASE_URL))
    from shared.database.core import Base

    create_database(engine.url)
    Base.metadata.create_all(engine)
    print('Database created successfully.')