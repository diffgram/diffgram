# OPENCORE - ADD
from shared.regular import regular_log
import datetime
import dateutil.parser
from shared.permissions.task_permissions import Permission_Task
import hmac


def input_check(spec, 
				log, 
				untrusted_input,
				string_len_not_zero=True
				):
	"""
	Check an untrusted variable

	TODO default checks
	vs more complicated ones (ie for String)

	The assumption is we get a dictionary from a request.
	We don't know if the key will be in the dictionary,
	or if it will be a reasonable input (ie not an empty string)

	It's annoying to have to do a bunch of these checks
	if we have many inputs, and we may easily add future checks here.

	Can just be type == None if doesn't matter

	Arguments
		spec, dict, variable name : type
		log, dict using boilerplate.log
		untrusted_input, dict of untrusted input

	Returns
		log
			Updated,
			errors are stored in log["error"][name] 
		ONE OF:
			Success case:
				Variable
			Failure case:
				none


	A spec dictionary may have a dictionary as a type
	If so, then it should have a 'default' and 'kind' key

	CAUTION if any issues with "," or syntax make sure there are the two
	closing brackets ie because the second one can be hard to see
	and often it quotes WRONG line number.
	  }
	}

	The default value will be filled if None is provided
	The kind will be used to type check

	spec_list_example = [{"name": str},
						 {"permission": {
							 'default': "all_secure_users",
							 'kind': str
							 }
						 },
						 {"label_mode" : {
							 'default': "closed_all_available",
							 'kind': str,
							 'required': True,
							 'valid_values_list': [],
							 'permission': 'task'
							 }
						 }]

	log, input, untrusted_input = regular_input.master(request=request,
													   spec_list=spec_list)
	if len(log["error"].keys()) >= 1:
		return jsonify(log=log), 400


	Supported permission checks:
		task

	Context of wanting to validate here is that prior we would 
	always use the wrapper (from the http url)
	and expect say the 'task_id' to be there.
	BUT in the context of post requests with more data, as we streamline that
	I prefer to validate and check the ids in the POST body.

	And in that context, it would be nicer to validate this upfront
	as trying to add the wrappers later is awkward.


	"""
	# QUESTION Do we want this?
	#if isinstance(spec, dict) is False:
	#	log["error"]["internal"] = True
	#	return log, None
	
	# non destructive here because we may reuse in list situations

	name, spec_and_default = next(iter(spec.items()))
	variable = untrusted_input.get(name, None)
	valid_values_list = None		# Caution this exposes valid values
	permission = None
	security_token = None	# Must match exactly. Does not expose valid value.
	allow_empty = False
	if isinstance(spec_and_default, dict):
		spec_type = spec_and_default.get('kind')
		default = spec_and_default.get('default')
		# user required, must have a value that's user supplied
		required = spec_and_default.get('required', False)	# Default to not required
		allow_empty = spec_and_default.get('allow_empty', False)	# Default to not required
		valid_values_list = spec_and_default.get('valid_values_list', None)

		permission = spec_and_default.get('permission')
		security_token = spec_and_default.get('security_token')

	else:
		spec_type = spec_and_default
		default = None
		if spec_type is not None:
			# If we do have a spec type, (either through new dict 
			# method, or straight listing it, then it's required.
			# We have to have default is None, since if we have a default
			# Then it's not required.
			required = True
		else:
			required = False

	# If there is no type
	# Then it's assumed to have a default value of None...
	# But historically we were using a None if spec_type
	# to indcate it was optional.
	# Let's not rush this... what if we want the default to be None?

	# If required is None, then we can just return the default.
	if variable and valid_values_list:
		if variable not in valid_values_list:
			log["error"]["valid_values_list"] = str(variable) + \
				" not in " + str(valid_values_list)
		# If it's "in the list" can we just return
		# instead of type checking?
		# I guess this is only really relevant to some types
		# like strings

	# What if variable is allowed to be None?
	if variable is None:
		if required is True:
			log["error"][name] = "Missing " + name
			return log, None, name
		else:
			# Note we return default instead of variable
			return log, default, name

	# Type checking
	if spec_type == str:
		if isinstance(variable, str) is False:
			log["error"][name] = "Must be string"
			return log, None, name

		if string_len_not_zero is True and not allow_empty:		
			if len(variable) == 0:
				log["error"][name] = "String " + name + \
					" must not be of length zero."
				return log, None, name

	elif spec_type == list:
		if isinstance(variable, list) is False:
			log["error"][name] = 'Must be a list'
			return log, None, name

		if len(variable) == 0 and not allow_empty:
			log["error"][name] = 'List must not be empty'
			return log, None, name

	elif spec_type == int:
		if isinstance(variable, int) is False:
			log["error"][name] = 'Must be an int'
			return log, None, name

	# Not clear about spectype name, but seems strange to pass "datetime" module
	# https://stackoverflow.com/questions/969285/how-do-i-translate-an-iso-8601-datetime-string-into-a-python-datetime-object

	elif spec_type == "datetime":
		try:
			variable = dateutil.parser.parse(variable)
		except:
			log["error"][name] = 'Must be ISO 8601 format. ie for Python try ' + \
				'using datetime.datetime.utcnow().isoformat()'
			return log, None, name

	elif spec_type == "date":
		is_valid_date = validate_date(variable)
		if not is_valid_date:
			log["error"][name] = "Incorrect data format, should be YYYY-MM-DD"

	if permission:
		validate_permission(permission, variable)

	if security_token:
		if validate_security_token(security_token, variable) is False:
			log['error']['security_token'] = False
			return log, None, name

	return log, variable, name


def validate_security_token(security_token, variable):
	if hmac.compare_digest(security_token, variable):
		return True
	return False	

def validate_permission(permission, variable):

	if permission == 'task':
		Permission_Task.by_task_id_core(variable)		


def validate_date(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def input_check_many(spec_list,
					 log,
					 untrusted_input,
					 string_len_not_zero=True):
	"""
	Want to check all names we expect
	that's why not using a .keys() method

	Arguments
		spec_list, a list of dicts to check
			format:
				variable name : type
				ex.
				{"name" : str}
		log, dict using regular.regular_log
		untrusted_input, dict of untrusted input

	Returns
		log
			Updated,
			errors are stored in log["error"][name] 

		input
			dict of variables where key is the name
			and value is value from untrusted dict OR None

	The assumption is that we run something like
	if len(log["error"].keys()) >= 1:
		return jsonify(log=log), 400
	"""
	input = {}

	if isinstance(untrusted_input, dict) is False:
		log["error"]["input"] = "Expecting dict"
		return log, None

	for spec in spec_list:
		log, variable, name = input_check( spec=spec, 
											log=log, 
											untrusted_input=untrusted_input,
											string_len_not_zero=string_len_not_zero
											)
		input[name] = variable

	return log, input



def master( request,
			spec_list,
			untrusted_input=None,
            string_len_not_zero = True
			):
	"""
	Combo init checker

	Creates log
	Gets json from request
	Runs input through check many

	Makes it safe to call dict['value'] directory from input
	And still pases "untrusted_input" in case we want values that 
	aren't being checked

	"""

	log = regular_log.default_api_log()

	if untrusted_input is None:
		try:
			untrusted_input = request.get_json(force=True)	
			# see http://flask.pocoo.org/docs/1.0/api/#flask.Request.get_json
		except:
			log["error"]["input"] = "Expecting json in request"
			return log, None, None

	log, input = input_check_many(spec_list=spec_list,
								  log=log,
								  untrusted_input=untrusted_input,
                                  string_len_not_zero = string_len_not_zero)
	
	return log, input, untrusted_input

