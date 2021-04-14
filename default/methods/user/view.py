# OPENCORE - ADD
from flask import render_template, flash
from flask import session as login_session
from methods import routes
from flask import render_template, url_for, flash, request, redirect, jsonify
from shared.database.user import User
from shared.helpers import sessionMaker
from shared.helpers.permissions import LoggedIn, getUserID, defaultRedirect
from shared.settings import settings
from shared.permissions.general import General_permissions


# SELF - current logged in user view

@routes.route('/user/view', methods=['GET'])
@General_permissions.grant_permission_for(['normal_user', 'super_admin'])
def user_view():       
    with sessionMaker.session_scope() as s:
        
        user = User.get(s)
        if user is None:
            return  jsonify({"none_found" : True}), 400, {'ContentType':'application/json'}

        out = jsonify(user=user.serialize())
        return out, 200, {'ContentType':'application/json'}


  
# Testing only other returns 400

@routes.route('/api/user/exists/<string:email>', methods = ['GET'])
@General_permissions.grant_permission_for(['allow_anonymous'])
def user_exists(email):
    if settings.DIFFGRAM_SYSTEM_MODE not in ['testing_e2e', 'testing', 'sandbox']:
        return jsonify(message='Invalid System Mode'), 400

    with sessionMaker.session_scope() as session:
        user = User.get_by_email(session, email)
        if user is None:
            return jsonify({"none_found": True}), 400, {'ContentType': 'application/json'}

        out = jsonify(found = True)

        return out, 200, {'ContentType': 'application/json'}

