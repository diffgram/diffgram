# OPENCORE - ADD
import string, hashlib, hmac, random
import binascii
import sys
from time import time

from shared.settings import settings

SECRET = settings.USER_PASSWORDS_SECRET



# For cookies

def hash_str(string__):
	start = time()

	string__ = bytearray(string__, 'utf-8')
	salt = bytearray(SECRET, 'utf-8')
	dk = hashlib.pbkdf2_hmac('sha512', string__, salt, 10000)
	hash = binascii.hexlify(dk)

	end = time()
	#print(end-start)
	return hash.decode("utf-8")


def make_secure_val(string__):
	string__ = str(string__)
	return f"{string__},{hash_str(string__)}"


def check_secure_val(secure_value):
	#payload , hash

	# TODO 
	# Should we be checking type here, ie str()

	secure_value_split = secure_value.split(',')
	if len(secure_value_split) != 2:
		return None

	payload = secure_value_split[0]
	outputted_hash = hash_str(payload)
	provided_hash = secure_value_split[1]

	if hmac.compare_digest(outputted_hash, provided_hash):
		return payload





# For password

def make_salt():
	init_salt = "jkl&&^22**j178&&"
	random_extra_salt = ''.join(random.choice(string.ascii_lowercase) for x in range(20))
	return init_salt + random_extra_salt


def make_password_hash(email, password, salt=None, iterations=None):
	if not salt:
		salt = make_salt()

	password = bytearray(email + password, 'utf-8')
	salt_byte = bytearray(salt, 'utf-8')

	if not iterations:
		iterations = random.randrange(50000, 100000)

	dk = hashlib.pbkdf2_hmac('sha512', password, salt_byte, iterations)
	hash = binascii.hexlify(dk).decode("utf-8")

	# Future, upgrade to Scrypt or Argon2

	return f"{hash},{salt},{iterations}"


def valid_password(email, attempted_password, hash):
	start = time()

	split_hash = hash.split(',')
	salt = split_hash[1]
	iterations = int(split_hash[2])
	attempted_hash = make_password_hash(email, attempted_password, salt, iterations)
	result = hmac.compare_digest(attempted_hash, hash)

	end = time()
	print(end-start)
	return result


