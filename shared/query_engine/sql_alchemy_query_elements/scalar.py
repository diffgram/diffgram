from shared.query_engine.sql_alchemy_query_elements.query_elements import QueryElement
from lark import Token
from sqlalchemy.orm import Session


class ScalarQueryElement(QueryElement):

    def build_query(self, session: Session, token: Token) -> ['ScalarQueryElement', dict]:

        # In case of an array:
        # Token value here is already a list. Parsed by array() function on sqlalchemy_query_executor.py
        # For rest of cases we just use the raw parsed value (either an int or str)
        value = token.value
        self.raw_value = value
