"""
    This script is useful for helm chart creation.
    To read more about helm setup read: https://diffgram.readme.io/docs/helm-kubernetes-installation
"""
from shared.settings import settings
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import create_engine


engine = create_engine(settings.DATABASE_URL)

print(f'Checking DB: {settings.DATABASE_URL}')
print(f"database_exists(engine.url) {database_exists(engine.url)}")

if not database_exists(engine.url):
    print(f'Creating DB: {settings.DATABASE_URL}')
    from shared.database.core import Base

    try:
        create_database(engine.url)
        Base.metadata.create_all(engine)
        print('Database created successfully.')
    except exception as e:
        print(f"{e}")
        print("Could not create")
else:
    print('Database already exists.')