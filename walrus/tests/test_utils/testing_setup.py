import time
start_time = time.time()
from flask import Flask
from flask_sslify import SSLify
from datetime import timedelta
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.settings import settings

# This line is to prevent developers to run test in other databases or enviroments. We should rethink how to handle
# configuration data for the different deployment phases (local, testing, staging, production)
if settings.DIFFGRAM_SYSTEM_MODE != 'testing':
    raise Exception('DIFFGRAM_SYSTEM_MODE must be in "testing" mode to perform any kind of test')


def create_walrus_testing_app():
    """
        Creates flask app for testing  the walrus
        with all the appropriate configuration
    :return:
    """
    from methods.input.upload import api_project_upload_large
    from methods.input.packet import input_packet
    from methods.input.input_view import input_list_web
    from methods.input.input_update import api_input_update
    from methods.export.export_web import web_export_to_file
    from methods.export.export_generation import new_external_export
    from methods.export.export_view import export_list
    from methods.video.interpolation import interpolate_all_frames
    from methods import routes as routes_blueprint
    from shared.helpers.security import limiter
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from shared.settings import settings
    app = Flask('Walrus Test',
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
        cls.app = create_walrus_testing_app()

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
