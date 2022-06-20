# OPENCORE - ADD

from methods.regular.regular_api import *

from shared.helpers.permissions import setSecureCookie

from shared.database.user import Signup_code
from shared.database.source_control.working_dir import WorkingDir

from methods import routes
from shared.permissions.general import General_permissions
from shared.permissions.project_permissions import Project_permissions
from shared.communicate.email import communicate_via_email
from shared.database import hashing_functions
from methods.user.account import account_verify

from methods.user.account import auth_code



verify_email_html_template = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"><html data-editor-version="2" class="sg-campaigns" xmlns="http://www.w3.org/1999/xhtml"> <head> <meta http-equiv="Content-Type" content="text/html; charset=utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1"> <!--[if !mso]><!--> <meta http-equiv="X-UA-Compatible" content="IE=Edge"> <!--<![endif]--> <!--[if (gte mso 9)|(IE)]> <xml> <o:OfficeDocumentSettings> <o:AllowPNG/> <o:PixelsPerInch>96</o:PixelsPerInch> </o:OfficeDocumentSettings> </xml> <![endif]--> <!--[if (gte mso 9)|(IE)]> <style type="text/css"> body {width: 600px;margin: 0 auto;} table {border-collapse: collapse;} table, td {mso-table-lspace: 0pt;mso-table-rspace: 0pt;} img {-ms-interpolation-mode: bicubic;} </style><![endif]--> <style type="text/css"> body, p, div { font-family: arial,helvetica,sans-serif; font-size: 14px; } body { color: #000000; } body a { color: #1188E6; text-decoration: none; } p { margin: 0; padding: 0; } table.wrapper { width:100% !important; table-layout: fixed; -webkit-font-smoothing: antialiased; -webkit-text-size-adjust: 100%; -moz-text-size-adjust: 100%; -ms-text-size-adjust: 100%; } img.max-width { max-width: 100% !important; } .column.of-2 { width: 50%; } .column.of-3 { width: 33.333%; } .column.of-4 { width: 25%; } ul ul ul ul { list-style-type: disc !important; } ol ol { list-style-type: lower-roman !important; } ol ol ol { list-style-type: lower-latin !important; } ol ol ol ol { list-style-type: decimal !important; } @media screen and (max-width:480px) { .preheader .rightColumnContent, .footer .rightColumnContent { text-align: left !important; } .preheader .rightColumnContent div, .preheader .rightColumnContent span, .footer .rightColumnContent div, .footer .rightColumnContent span { text-align: left !important; } .preheader .rightColumnContent, .preheader .leftColumnContent { font-size: 80% !important; padding: 5px 0; } table.wrapper-mobile { width: 100% !important; table-layout: fixed; } img.max-width { height: auto !important; max-width: 100% !important; } a.bulletproof-button { display: block !important; width: auto !important; font-size: 80%; padding-left: 0 !important; padding-right: 0 !important; } .columns { width: 100% !important; } .column { display: block !important; width: 100% !important; padding-left: 0 !important; padding-right: 0 !important; margin-left: 0 !important; margin-right: 0 !important; } .social-icon-column { display: inline-block !important; } } </style> <style> @media screen and (max-width:480px) { table\0 { width: 480px !important; } } </style> <!--user entered Head Start--><!--End Head user entered--> </head> <body> <center class="wrapper" data-link-color="#1188E6" data-body-style="font-size:14px; font-family:arial,helvetica,sans-serif; color:#000000; background-color:#FFFFFF;"> <div class="webkit"> <table cellpadding="0" cellspacing="0" border="0" width="100%" class="wrapper" bgcolor="#FFFFFF"> <tr> <td valign="top" bgcolor="#FFFFFF" width="100%"> <table width="100%" role="content-container" class="outer" align="center" cellpadding="0" cellspacing="0" border="0"> <tr> <td width="100%"> <table width="100%" cellpadding="0" cellspacing="0" border="0"> <tr> <td> <!--[if mso]> <center> <table><tr><td width="600"> <![endif]--> <table width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%; max-width:600px;" align="center"> <tr> <td role="modules-container" style="padding:0px 0px 0px 0px; color:#000000; text-align:left;" bgcolor="#FFFFFF" width="100%" align="left"><table class="module preheader preheader-hide" role="module" data-type="preheader" border="0" cellpadding="0" cellspacing="0" width="100%" style="display: none !important; mso-hide: all; visibility: hidden; opacity: 0; color: transparent; height: 0; width: 0;"> <tr> <td role="module-content"> <p></p> </td> </tr> </table><table class="module" role="module" data-type="spacer" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="7d11ec12-8d1c-4f5c-a687-9dd298eece0d"> <tbody> <tr> <td style="padding:0px 0px 30px 0px;" role="module-content" bgcolor=""> </td> </tr> </tbody> </table><table class="wrapper" role="module" data-type="image" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="36ec412d-e803-4e26-868d-06d7109ffd1b"> <tbody> <tr> <td style="font-size:6px; line-height:10px; padding:0px 0px 0px 0px;" valign="top" align="center"> <a href="https://diffgram.com"><img class="max-width" border="0" style="display:block; color:#000000; text-decoration:none; font-family:Helvetica, arial, sans-serif; font-size:16px; max-width:50% !important; width:50%; height:auto !important;" width="300" alt="Diffgram Web" data-proportionally-constrained="true" data-responsive="true" src="http://cdn.mcauto-images-production.sendgrid.net/af131d949b78b171/f575494f-6d94-44fe-bf0e-7c0987f50441/1181x418.png"></a></td> </tr> </tbody> </table><table class="module" role="module" data-type="spacer" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="409d4638-4890-4128-b43e-20ca56e8c58a"> <tbody> <tr> <td style="padding:0px 0px 30px 0px;" role="module-content" bgcolor=""> </td> </tr> </tbody> </table><table class="module" role="module" data-type="text" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="6d8c86cd-d253-42c7-964d-dc7d9beced2c" data-mc-module-version="2019-10-22"> <tbody> <tr> <td style="padding:18px 0px 18px 0px; line-height:22px; text-align:inherit;" height="100%" valign="top" bgcolor="" role="module-content"><div><div style="font-family: inherit; text-align: center"><span style="color: #202020; font-size: 36px">Welcome</span>&nbsp;</div><div></div></div></td> </tr> </tbody> </table><table class="module" role="module" data-type="spacer" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="1598987a-d47a-47d8-bb9a-a9ee312882c0"> <tbody> <tr> <td style="padding:0px 0px 30px 0px;" role="module-content" bgcolor=""> </td> </tr> </tbody> </table><table border="0" cellpadding="0" cellspacing="0" class="module" data-role="module-button" data-type="button" role="module" style="table-layout:fixed;" width="100%" data-muid="787ee574-490f-47e2-bc7d-739ca07b21a1"> <tbody> <tr> <td align="center" bgcolor="" class="outer-td" style="padding:0px 0px 0px 0px;"> <table border="0" cellpadding="0" cellspacing="0" class="wrapper-mobile" style="text-align:center;"> <tbody> <tr> <td align="center" bgcolor="#3b8aca" class="inner-td" style="border-radius:6px; font-size:16px; text-align:center; background-color:inherit;"> <a href="http://verify_http_link" style="background-color:#3b8aca; border:0px solid #333333; border-color:#333333; border-radius:6px; border-width:0px; color:#ffffff; display:inline-block; font-size:29px; font-weight:normal; letter-spacing:0px; line-height:normal; padding:12px 18px 12px 18px; text-align:center; text-decoration:none; border-style:solid;" target="_blank">Verify Email Now</a> </td> </tr> </tbody> </table> </td> </tr> </tbody> </table><table class="module" role="module" data-type="text" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="674c5d71-ec72-48de-9853-431f415ffb63" data-mc-module-version="2019-10-22"> <tbody> <tr> <td style="padding:18px 160px 18px 160px; line-height:10px; text-align:inherit;" height="100%" valign="top" bgcolor="" role="module-content"><div><div style="font-family: inherit; text-align: center"><span style="font-size: 8px">Or copy and paste this into your browser:</span></div><div style="font-family: inherit; text-align: center"><span style="font-size: 8px">&nbsp;</span></div><div style="font-family: inherit; text-align: center"><span style="font-size: 8px">http://verify_http_link</span></div><div></div></div></td> </tr> </tbody> </table><table class="module" role="module" data-type="spacer" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="2732c18c-02c9-4b7c-a6a5-36fb604e5781"> <tbody> <tr> <td style="padding:0px 0px 120px 0px;" role="module-content" bgcolor=""> </td> </tr> </tbody> </table><table class="module" role="module" data-type="text" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="2e093e01-2c42-4789-b3c4-410b0d5ea0a7" data-mc-module-version="2019-10-22"> <tbody> <tr> <td style="padding:18px 0px 18px 0px; line-height:22px; text-align:inherit;" height="100%" valign="top" bgcolor="" role="module-content"><div><div style="font-family: inherit; text-align: center"><span style="font-size: 14px">Diffgram Inc.</span></div><div style="font-family: inherit; text-align: center"><span style="font-size: 14px">Made with ❤️ from all over the 🌎🌍🌏</span></div><div></div></div></td> </tr> </tbody> </table><table class="module" role="module" data-type="social" align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="7d733169-43c9-4189-bae3-d46670ff4512"> <tbody> <tr> <td valign="top" style="padding:0px 0px 0px 0px; font-size:6px; line-height:10px;" align="center"> <table align="center" style="-webkit-margin-start:auto;-webkit-margin-end:auto;"> <tbody><tr align="center"><td style="padding: 0px 5px;" class="social-icon-column"> <a role="social-icon-link" href="https://twitter.com/diffgram" target="_blank" alt="Twitter" title="Twitter" style="display:inline-block; background-color:#7AC4F7; height:21px; width:21px;"> <img role="social-icon" alt="Twitter" title="Twitter" src="https://mc.sendgrid.com/assets/social/white/twitter.png" style="height:21px; width:21px;" height="21" width="21"> </a> </td><td style="padding: 0px 5px;" class="social-icon-column"> <a role="social-icon-link" href="https://www.linkedin.com/company/diffgram/" target="_blank" alt="LinkedIn" title="LinkedIn" style="display:inline-block; background-color:#0077B5; height:21px; width:21px;"> <img role="social-icon" alt="LinkedIn" title="LinkedIn" src="https://mc.sendgrid.com/assets/social/white/linkedin.png" style="height:21px; width:21px;" height="21" width="21"> </a> </td></tr></tbody> </table> </td> </tr> </tbody> </table><table class="module" role="module" data-type="spacer" border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed;" data-muid="bd456f0d-a249-435b-ad68-1c992b66b5dd"> <tbody> <tr> <td style="padding:0px 0px 30px 0px;" role="module-content" bgcolor=""> </td> </tr> </tbody> </table></td> </tr> </table> <!--[if mso]> </td> </tr> </table> </center> <![endif]--> </td> </tr> </table> </td> </tr> </table> </td> </tr> </table> </div> </center> </body> </html>"""


@routes.route('/api/v1/user/verify', 
			  methods=['POST'])
@limiter.limit("3 per day")
def redeem_verify_via_email_api():  
	"""
	TODO clarify this is verifying an account

	"""

	code_proposed = None
	project_string_id = None

	with sessionMaker.session_scope() as session:

		log = {}
		log['success'] = False
		log['error'] = {}

		data = request.get_json(force=True)
		email_proposed = data.get('email', None)
		auth_code_proposed = data.get('auth_code', None)

		if auth_code_proposed:
			result, message, auth = auth_code.attempt_redeem_code(	session,
																	auth_code_proposed, 
																	email_proposed)
			if result == False:
				log['error']['auth_code'] = message
				return jsonify(log = log), 200

		log['success'] = True

		return jsonify(log = log), 200


@routes.route('/api/v1/user/verify/is_email_confirmed', 
			  methods=['GET'])
@General_permissions.grant_permission_for(['normal_user'])
def is_email_confirmed_api():

	log = regular_input.regular_log.default_api_log()
	security_email_verified = False
	with sessionMaker.session_scope() as session:

		user = User.get(session)
		security_email_verified = user.security_email_verified
		log['success'] = True

	return jsonify(log = log,
                security_email_verified = security_email_verified), 200


@routes.route('/api/v1/user/verify/start', 
			  methods=['GET'])
@limiter.limit("2 per day")
@General_permissions.grant_permission_for(['normal_user'])
def start_verify_via_email_api():

	# TODO what other limits here??
	
	# TODO verify case of user who has multiple outstanding auth codes
	# ie is it resending same code or?

	log = regular_input.regular_log.default_api_log()

	with sessionMaker.session_scope() as session:

		user = User.get(session)


		result, log = start_verify_via_email( session = session, 
												user = user,
												log = log)
		if result is False:
			return jsonify(log = log), 400

	log['success'] = True
	return jsonify(log = log), 200



def start_verify_via_email( session, 
						    user,
							log=None):
		"""
		Goal
			Verify a user's email address is real
			Send code to email, expecting to be redeemed by 
			redeem_verify_via_email()

		Arguments
			session, db session
			user, class User() object

		"""
		if user.security_email_verified is True:
			log['error']['verify_error'] = "Already verified."
			return False, log

		result, message, auth = auth_code.new(session = session,
											 user = user,
											 email_sent_to = user.email,
											 auth_code_type = "verify_signup")

		# Autofix domains that don't end with /
		url_base = settings.URL_BASE

		if not url_base.endswith('/'):
			url_base += '/'

		link_verify = f"{url_base}user/account/verify_email/{auth.email_sent_to}/{auth.code}"

		subject = "Verify Your Diffgram Account Now"

		message = f"Welcome, please verify your Diffgram account now {link_verify}"
		
		message += " "

		global verify_email_html_template
		verify_email_html = verify_email_html_template
		verify_email_html = verify_email_html.replace('http://verify_http_link', link_verify)
		

		communicate_via_email.send(email = user.email, 
								   subject = subject, 
								   message = message,
                                   html = verify_email_html)

		return True, log
