# OPENCORE - ADD
import datetime


class Stats():


	def fill_missing_dates(date_from, 
						   date_to, 
						   list_by_period):

		"""
		date_from, a python datetime.datetime object?

		"""

		# CAREFUL
		# ASSUMES *assending* ORDERED!!!!! (

		# TODO not quite generic yet, "day" focused in a few areas

		with_missing_dates = []

		# Maybe take this out and just enforce is datetime?
		# This was from prior issues with midnight / date_to
		if isinstance(date_from, datetime.datetime) is False:
			date_from = datetime.datetime.strptime(date_from,  "%Y-%m-%d")
			date_to = datetime.datetime.strptime(date_to,  "%Y-%m-%d")
		
		next_date = date_from

		period = (date_to - date_from).days
	
		len_task_list = len(list_by_period)

		#print(list_by_period)


		index = 0
		for i in range(period):

			# Careful to use .date() here to only compare date otherwise
			# time thing can mess it up?

			# What is date() is doing? 
			# Answer: docs says "Return date object with same year, month and day."
			# https://docs.python.org/3.5/library/datetime.html#datetime.datetime.date

			if index + 1 <= len_task_list and list_by_period[index][0].date() == next_date.date():	
			
				with_missing_dates.append(list_by_period[index]) 
				index += 1

			else:			
				with_missing_dates.append((next_date, 0))
				
			next_date = next_date + datetime.timedelta(days=1)

		return with_missing_dates