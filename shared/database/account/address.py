from shared.database.common import *


class Address(Base):
	__tablename__ = 'address'

	"""
	
	"""

	id = Column(Integer, primary_key=True)

	line_1 = Column(String)		# Number,   100
	line_2 = Column(String)		# Street name,  Road Pl
	line_3 = Column(String)		# Building, Floor, and UNit,  APT 1
	line_4 = Column(String)		# Optional

	locality = Column(String)	# City,  Santa Clara
	region = Column(String)		# State,  CA
	postcode = Column(String)	# ZIP 95051

	country = Column(String)		# USA


	# Concept that we create a new address object upon changes,
	# So as to keep old info?

	previous_address_id = Column(Integer, ForeignKey('address.id'))
	previous_address = relationship('Address', 
									foreign_keys=[previous_address_id])

	member_created_id = Column(Integer, ForeignKey('member.id')) 
	member_created = relationship("Member", foreign_keys=[member_created_id])

	time_created = Column(DateTime, default=datetime.datetime.utcnow)

