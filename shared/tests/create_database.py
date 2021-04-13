# OPENCORE - ADD
from shared.settings import settings
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy_utils.functions import drop_database
from sqlalchemy import create_engine


engine = create_engine(settings.DATABASE_URL)
print('Checking DB: {}'.format(settings.DATABASE_URL))

if not database_exists(engine.url):
    print('Creating DB: {}'.format(settings.DATABASE_URL))
    from shared.database.core import Base
    create_database(engine.url)
    Base.metadata.create_all(engine)
    print('Database created successfully.')
else:
    print('Database already exists.')
