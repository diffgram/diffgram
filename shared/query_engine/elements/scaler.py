
class ScalerQueryElement(QueryElement):

    def __init__(self):

    def something()
        if type(formatted_entity) != str:
            q.is_reserved_word = False
            q.type = 'scalar'
            q.token = token
            q.project_id = project_id
            return q

    @staticmethod
    def create_from_token(session: Session, project_id: int, log: dict, token: Token) -> ['ListQueryElement', dict]:
        # Token value here is already a list. Parsed by array() function on sqlalchemy_query_executor.py
        list_value = token.value
        if type(list_value) != list:
            log['error']['list_value'] = f'Invalid token value {token.value}. Not a list.'
            return None, log
        query_element = ListQueryElement(list_value = list_value)
        return query_element, log