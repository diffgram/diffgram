# OPENCORE - ADD
from shared.database.common import *


class new_instance(Base):

	# TO be added directly into instance?
	# (so as to use file system stuff?)


	# Translation

	# Why would this be a float if dealing in pixel space?
	# Don't declare as translation for readabilty
	# Center point
	x = Column(Integer)
	y = Column(Integer)
	z = Column(Integer)

	# Size
	width = Column(Float)
	length = Column(Float)
	height = Column(Float)

	# Rotation
	# Quaterions
	a = Column(Float)
	b = Column(Float)
	c = Column(Float)
	d = Column(Float)

	# Visibilty
	# Do want this as a foreign key to a "visiblity" class?
	# How would this relate to 2d things?
	# (Same with attributes)

	visibility_level = Column(Integer)

	# Group of instances through time
	group = Column()

	# next / previous?





