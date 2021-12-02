from shared.database.common import *


class Transaction(Base):
	__tablename__ = 'transaction'

	"""

	A single atomic unit of measurement, related to an Account.
	
	"""

	id = Column(Integer, primary_key=True)

	account_id = Column(Integer, ForeignKey('account.id'))
	account = relationship('Account', 
							foreign_keys=[account_id])

	transaction_previous_id = Column(Integer, ForeignKey('transaction.id'))
	transaction_previous = relationship(	'Transaction', 
											foreign_keys=[transaction_previous_id],
											uselist=False)

	# Related / linked transaction?
	transaction_related_id = Column(Integer, ForeignKey('transaction.id'))
	transaction_related = relationship('Transaction', 
											foreign_keys=[transaction_related_id])

	# TODO do we need to add a "unit type" here? 
	# ie Dollars, time, whole units, or...

	transaction_type = Column(String)		# TODO rename to kind
	# "task", "brain", "general"

	sub_kind = Column(String)	# New May 20, 2019

	amount = Column(Integer)
	"""
	Signed amount
	where Credit == positive
	and Debit == negative

	100 = $1.00
	See https://stackoverflow.com/questions/3730019/why-not-use-double-or-float-to-represent-currency
	"""

	balance_new = Column(Integer)		 # Balance after transaction?

	cost_per_instance = Column(Integer)
	count_instances_changed = Column(Integer)

	task_id = Column(Integer, ForeignKey('task.id'))
	task = relationship('Task', 
							foreign_keys=[task_id])

	job_id = Column(Integer, ForeignKey('job.id'))		# Cache from task
	job = relationship('Job', 
							foreign_keys=[job_id])


	# New May 29, 2019
	project_id = Column(Integer, ForeignKey('project.id'))
	project = relationship('Project', 
							foreign_keys=[project_id])

	time_created = Column(DateTime, default=datetime.datetime.utcnow)
	time_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)

	# New April 2, 2019
	audit_cache =  Column(MutableDict.as_mutable(JSONEncodedDict), 
							default = {})


	def new(	session,
			account,
			transaction_type,
			amount,
			task = None,
			audit_cache = None,
			sub_kind = None,
			time_created = None,
			project_id = None
			):
		"""

		Create a transaction object

		audit_cache is a place to store info about the transaction

		Feels like bad idea to allow time_created to be modified...
		But in context of being able to declare time_created
		for usage cycle... maybe in future this should be
		a seperate field?
		
		"""

		# TODO handle if account is none? / check? hmmm


		transaction_previous = account.transaction_previous
		transaction_previous_id = None

		if transaction_previous:
			balance_new = amount + transaction_previous.balance_new

			# Caution, cache id here otherwise sqlaclchemy gets confused
			transaction_previous_id = transaction_previous.id
		else:
			balance_new = amount

		transaction = Transaction(account = account,							
								  amount = amount,
								  transaction_previous_id = transaction_previous_id,
								  transaction_type = transaction_type,
								  balance_new = balance_new,
								  sub_kind = sub_kind
								  )

		# Don't really need if statements here right?
		# SQL alchemy just handles it

		if audit_cache:
			transaction.audit_cache = audit_cache

		if time_created:
			transaction.time_created = time_created

		transaction.project_id = project_id

		session.add(transaction)

		if task:
			transaction.task = task
			transaction.job_id = task.job_id
			transaction.count_instances_changed = task.count_instances_changed

		session.flush()

		account.transaction_previous_id = transaction.id
		session.add(account)

		return transaction


	def serialize_for_account(self):

		return {
			'id' : self.id,
			'balance_new' : self.balance_new
		}


	def serialize_for_list_view_builder(self):

		# May want to provide more info ie what job
		# Be able to link to task etc.

		return {
			'id' : self.id,
			'amount' : self.amount,
			'balance_new' : self.balance_new,
			'cost_per_instance' : self.cost_per_instance,
			'count_instances_changed' : self.count_instances_changed,
			'task_id' : self.task_id,
			'job_id' : self.job_id,
			'time_created' : self.time_created
		}


	@staticmethod
	def check_limits(account, 
					 amount, 
					 credit_limit=0):
		"""
		False, failed
        True, succedded

		account, db Account object
		amount, integer

		optional
		credit_limit, defaults to 0, to extend up to 10 units of credit set to 10


		"""

		# TODO logging...

		# Assumes adding?
		if not account or not amount:
			return False, "No account or amount"

		transaction_previous = account.transaction_previous

		if not transaction_previous:
			return False, "No transaction previous"

		balance_new = transaction_previous.balance_new

		trial_balance = balance_new + amount

		#print("balance_new", balance_new, "trial_balance", trial_balance)

		trial_balance -= credit_limit

		#print("trial_balance", trial_balance)

		if trial_balance > 0:
			return False, "Trial balance > 0"

		return True, None
		




