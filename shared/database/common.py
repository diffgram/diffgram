# OPENCORE - ADD
"""
These are shared among all of the shared.database files
Doesn't make sense to import these individual when resused many times
Any imports here must be safe for:

from shared.database.common import *



"""
import sys
import datetime
import time

from sqlalchemy import Column
from sqlalchemy import BIGINT
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Boolean
from sqlalchemy import ARRAY
from sqlalchemy.dialects.postgresql import JSONB, JSON

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.orm import deferred
# https://docs.sqlalchemy.org/en/13/orm/loading_columns.html?highlight=deferred%20loading

from sqlalchemy.ext.mutable import Mutable

from shared.database.core import MutableDict
from shared.database.core import JSONEncodedDict

from shared.settings import settings

from shared.database.core import Base
from shared.database.caching import Caching
from shared import data_tools_core
from sqlalchemy import or_

from shared.regular import regular_methods


data_tools = data_tools_core.Data_tools().data_tools
