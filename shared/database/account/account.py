from shared.database.common import *


class Account(Base):
	__tablename__ = 'account'

	"""

	An abstract holding object for transactions.
	For example, could be declared as  "billing" account.
	And link to billing transactions
	
	"""

	# Balance is stored in transaction_previous.balance_new

	id = Column(Integer, primary_key=True)

	nickname = Column(String)

	mode_trainer_or_builder = Column(String)  # 'trainer', 'builder'

	account_type = Column(String)		#  'billing'
	
	# or "CASH" or "Billing"?  # "Invoice" / monthly...
	# This should be differet from type?

	credit_limit = Column(Integer)

	payment_method_on_file = Column(Boolean)

	security_disable = Column(Boolean)

	transaction_previous_id = Column(Integer, ForeignKey('transaction.id'))
	transaction_previous = relationship('Transaction', 
										foreign_keys=[transaction_previous_id])


	address_primary_id = Column(Integer, ForeignKey('address.id'))
	address_primary = relationship('Address', 
										foreign_keys=[address_primary_id])

	primary_user_id = Column(Integer, ForeignKey('userbase.id'))
	primary_user = relationship('User', 
								foreign_keys=[primary_user_id])

	# org_id = Column(Integer, ForeignKey('org.id'))
	# org = relationship('Org', foreign_keys=[org_id])

	stripe_id = Column(String)

	
	member_created_id = Column(Integer, ForeignKey('member.id')) 
	member_created = relationship("Member", foreign_keys=[member_created_id])

	member_updated_id = Column(Integer, ForeignKey('member.id'))
	member_updated = relationship("Member", foreign_keys=[member_updated_id])

	time_created = Column(DateTime, default=datetime.datetime.utcnow)
	time_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)


	def get_by_id(	session, 
					account_id):
		
		if account_id is None:
			return False

		return session.query(Account).filter(
					Account.id == account_id).first()


	def get_list(	session,
					mode_trainer_or_builder,				
					user_id=None,
					account_type=None,
					by_primary_user=True
					):
		"""
		mode_trainer_or_builder ['trainer', 'builder']

		Only supports by_primary_user at the moment
		"""

		# Do we actually need this check?
		if user_id is None:
			return False

		if mode_trainer_or_builder is None:
			return False

		if by_primary_user is True:
				
			query = session.query(Account).filter(
							Account.primary_user_id == user_id)

		if account_type:
			query = query.filter(Account.account_type == account_type)

		query = query.filter(Account.mode_trainer_or_builder == mode_trainer_or_builder)

		return query.all()


	def serialize(self):

		transaction_previous_serialized = None

		if self.transaction_previous:
			transaction_previous_serialized = self.transaction_previous.serialize_for_account()

		return {
			'id' : self.id,
			'nickname' : self.nickname,
			'account_type': self.account_type,
			'transaction_previous' : transaction_previous_serialized,
			'payment_method_on_file' : self.payment_method_on_file
			}


	@staticmethod
	def account_new_core(
			session,
			primary_user,
			mode_trainer_or_builder,
			account_type = None,
			nickname = "My Account"):
		"""

		
		"""


		account = Account(	nickname = nickname,
							mode_trainer_or_builder = mode_trainer_or_builder,
							account_type = account_type,
							primary_user = primary_user,
							member_created_id = primary_user.member_id)
		session.add(account)

		return account