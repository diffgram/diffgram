# OPENCORE - ADD
from flask import session as login_session
from flask import redirect
from methods import routes


@routes.route('/user/logout', methods=['GET'])
def logout():
    login_session['user_id'] = ''
    return "Success", 200

