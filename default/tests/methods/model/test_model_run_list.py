from typing import Dict, List

import json
import b64encode
from unittest.mock import patch

from methods.regular.regular_api import ModelRunListLog
from default.tests.test_utils import DiffgramBaseTestCase, testing_setup
from shared.tests.test_utils import common_actions, data_mocking
from shared.database.model.model_run import ModelRun
from shared.database.model.model import Model
from base64 import b6
