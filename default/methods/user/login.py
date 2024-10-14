# This is the login route for the application, which supports both password and magic link authentication methods.
# It also supports One Time Password (OTP) for added security.
@routes.route('/api/user/login', methods=['POST'])
@limiter.limit("40 per hour, 120 per day")
def login():
    """
    Shared method for either magic link or password
    Supports one time pass (OTP)

    """
    # Create a new login history record in the database with success = False
    log = {'success': False, 'error': {}}

    # Get the request data
    data = request.get_json(force=True)

    # Get the mode of authentication from the request data
    mode = data.get('mode', None)

    # Check if the mode is valid
    if mode is None or len(mode) == 0:
        log['error']['mode'] = "No mode"
        return jsonify(log=log), 400

    if mode not in ["password", "magic_auth_redeem"]:
        log['error']['mode'] = "Invalid mode"
        return jsonify(log=log), 400

    # Check if the user exists for password mode
    if mode == "password":
        user_email_proposed = data.get('email', None)
        if user_email_proposed is None or len(user_email_proposed) == 0:
            log['error']['email'] = "No email provided"
            return jsonify(log=log), 400

        user_password_proposed = data.get('password', None)
        if user_password_proposed is None or len(user_password_proposed) == 0:
            log['error']['password'] = "No password"
            return jsonify(log=log), 400

        user_email_proposed = user_email_proposed.lower()
        user = session.query(User).filter_by(email=user_email_proposed).first()

        if user is None:
            log['error']['email'] = "Invalid email"
            return jsonify(log=log), 400

        # Check if the user has exceeded the maximum number of password attempts
        if user.password_attempt_count >= settings.MAX_PASSWORD_ATTEMPTS_BEFORE_LOCKOUT:
            log['error']['email'] = "Please contact us to unlock account. (Too many attempts.)"
            return jsonify(log=log), 400

        # Check if the provided password is correct
        if user.password_hash is None:
            log['error']['password'] = "No password set. Use magic link to login."
            return jsonify(log=log), 400

        password_result = hashing_functions.valid_password(user_email_proposed,
                                                           user_password_proposed,
                                                           user.password_hash)

        if password_result is False:
            # Update the user's login history with success = False
            User.new_login_history(session=session,
                                   success=False,
                                   otp_success=None,
                                   remote_address=request.remote_addr,
                                   user_id=user.id)
            session.add(user)

            log['error']['password'] = "Invalid password"
            user.password_attempt_count += 1
            session.add(user)
            return jsonify(log=log), 400

    # Check if the provided magic link is valid
    if mode == "magic_auth_redeem":
        magic_auth_proposed = data.get('auth_code', None)
        if magic_auth_proposed is None or len(magic_auth_proposed) == 0:
            log['error']['magic'] = "No auth code"
            return jsonify(log=log), 400

        # Check if the provided magic link is valid
        result, message, auth = auth_code.attempt_redeem_code(session=session,
                                                              auth_code=magic_auth_proposed)
        if result is False:
            log['error']['magic'] = message
            return jsonify(log=log), 200

        # Get the user associated with the magic link
        user = session.query(User).filter_by(email=auth.email_sent_to).first()

    # Update the user's login history with success = True
    User.new_login_history(session=session,
                           success=True,
                           otp_success=None,
                           remote_address=request.remote_addr,
                           user_id=user.id)
    session.add(user)
    user.password_attempt_count = 0

    log["success"] = True

    # Check if OTP is enabled for the user
    if user.otp_enabled is True:
        user.otp_current_session = pyotp.random_base32()
        user.otp_current_session_expiry = int(time.time()) + 180

        # Passing email for use with OTP
        return jsonify(log=log,
                       otp_prompt=True,
                       user_email=user.email,
                       otp_current_session=user.otp_current_session), 200

    # Check if OAuth2 is enabled
    if user.otp_enabled is None or user.otp_enabled is False:
        if settings.USE_OAUTH2:
            if not jwt:
                log['error']['login'] = 'OAUTH2 Login is enabled. Cannot use default login. Please use SSO or contact your admin.'
                return jsonify(log=log), 400
            set_jwt_in_session(jwt)
        else:
            setSecureCookie(user)
        result = {
            'log': log,
            'user': user.serialize(),
            'access_token_data': access_token_data,
            'user_data_oidc': user_data_oidc,
            'install_fingerprint': settings.DIFFGRAM_INSTALL_FINGERPRINT
        }
        logger.debug(f'Log in success result {result}')
        return jsonify(result), 200
