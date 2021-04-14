# OPENCORE - ADD
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator
from sqlalchemy.types import  VARCHAR
import json
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.dialects.postgresql import ARRAY


Base = declarative_base()


class JSONEncodedDict(TypeDecorator):
    "Represents an immutable structure as a json-encoded string."

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value



class MutableDict(Mutable, dict):
    """
    See https://docs.sqlalchemy.org/en/13/orm/extensions/mutable.html
    CAUTION this will fail to detect some cases
     eg children fails (here self.frame_number is the child)
        parent_input.update_log['error'][self.frame_number] = error_log

     One work around is to trigger an update on the dict
     parent_input.update_log['last_updated'] = str(time.time())

     (Then it seems to detect rest of children events)

    """
    @classmethod
    def coerce(cls, key, value):
        "Convert plain dictionaries to MutableDict."

        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        "Detect dictionary set events and emit change events."

        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        "Detect dictionary del events and emit change events."

        dict.__delitem__(self, key)
        self.changed()

