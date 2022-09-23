# OPENCORE - ADD
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request

limiter = Limiter(  key_func = get_remote_address,
					default_limits = ["6000000 per day", "900000 per hour", "10000 per second"],
					headers_enabled = True
					)