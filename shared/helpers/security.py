# OPENCORE - ADD
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request

limiter = Limiter(  key_func = get_remote_address,
					default_limits = ["20000 per day", "9000 per hour"],
					headers_enabled = True
					)