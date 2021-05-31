# OPENCORE - ADD
import random

from default.methods.regular.regular_api import *
from shared import database_setup_supporting		
import numpy as np

from connection_operations import Connection_Operations


@dataclass
class Test():
	session: Any
	project: Any = None

	def __post_init__(self):

		self.log = regular_log.default()
		self.try_to_commit = regular_methods.try_to_commit

	# WIP not updated
	def __del__(self):
		# Clean up
		# actually in this case we don't want to delete input because
		# we expect that process_media will handle that
		"""
		try:
			self.session.delete(self.input)
		except:
			# can't delete if it's not persisted
			# otherwise this throws funny exception message
			pass
		"""



	def mock_decryption(self):

		import difflib

		connection_id = 10

		connection_operations = Connection_Operations(
			session = self.session,
			connection_id = connection_id
			)

		connection_operations.get_existing_connection(connection_id)

		print(connection_operations.connection.private_secret_encrypted)

		decrypted_secret = connection_operations.get_secret()

		assert connection_operations.connection.private_secret_encrypted != decrypted_secret

		sandbox_key = "\n"
		def diff(a, b):
			for i,s in enumerate(difflib.ndiff(a, b)):
				if s[0]==' ': continue
				elif s[0]=='-':
					print(u'Delete "{}" from position {}'.format(s[-1],i))
				elif s[0]=='+':
					print(u'Add "{}" to position {}'.format(s[-1],i))  

		# Diff falsely fails here....

		#diff(decrypted_secret, sandbox_key)
		# https://stackoverflow.com/questions/46280148/python-3-x-dont-count-carriage-returns-with-len
		# assert with carraige returns?

		print(len(decrypted_secret), len(sandbox_key))
		assert decrypted_secret == sandbox_key
		#assert decrypted_secret == "test"



	def mock_date(self):
		pass

		# TODO mock date and attach to report?


	def mock_source(self, id):
		"""
		"""
		project_string_id = None
		scope = None
		private_secret = "Super secret"
		private_id = "1"

		metadata = {
			'project_string_id': project_string_id,
			'private_id' : private_id,
			'private_secret': private_secret,
			}

		return metadata

	
	def test_create_new_source(self):
		"""
		Feb 5, 2020
		 So one issue is this misses some of validation that
		 front end stuff does...
		"""
	
		source_id = None

		metadata = self.mock_report(id = id)

		self.source_operations = Source_Operations(
				session = self.session,
				source_id = source_id,
				metadata = metadata
				)

		self.source_operations.save()

		assert self.source_operations.source.id is not None




def test():

	with sessionMaker.session_scope() as session:

		project = Project.get_by_string_id(
			session,
			"patternantelope")

		test = Test(session, 
					project=project)
		test.mock_decryption()


test()


