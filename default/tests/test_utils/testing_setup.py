import time
start_time = time.time()
from flask import Flask
from flask_sslify import SSLify
from datetime import timedelta
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.settings import settings
from routes_init import do_routes_importing
# This line is to prevent developers to run test in other databases or enviroments. We should rethink how to handle
# configuration data for the different deployment phases (local, testing, staging, production)
if settings.DIFFGRAM_SYSTEM_MODE != 'testing':
    raise Exception('DIFFGRAM_SYSTEM_MODE must be in "testing" mode to perform any kind of test')

def create_default_testing_app():
    """
        Creates flask app for testing  the walrus
        with all the appropriate configuration
    :return:
    """

    do_routes_importing()
    from methods import routes as routes_blueprint
    from shared.helpers.security import limiter
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from shared.settings import settings
    app = Flask('Default Test App',
                static_folder="./dist/static",
                template_folder="./dist")
    # sslify = SSLify(app, subdomains=True)
    app.register_blueprint(routes_blueprint)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=14)
    app.secret_key = settings.SECRET_KEY
    limiter.init_app(app)
    return app


class DiffgramBaseTestCase(unittest.TestCase):
    db = None

    if settings.DIFFGRAM_SYSTEM_MODE != 'testing':
        raise Exception('Diffgram Environment must be in "testing" mode to perform any kind of test')

    @classmethod
    def setUpClass(cls):
        super(DiffgramBaseTestCase, cls).setUpClass()
        cls.engine = create_engine(settings.DATABASE_URL)
        cls.session_factory = sessionmaker(bind=cls.engine)
        cls.app = create_default_testing_app()

    @classmethod
    def tearDownClass(cls):
        super(DiffgramBaseTestCase, cls).tearDownClass()

    def setUp(self):
        super(DiffgramBaseTestCase, self).setUp()
        self.app.testing = True
        self.client = self.app.test_client()
        self.session = self.session_factory()

    def tearDown(self):
        self.session.rollback()
        self.session.close()
