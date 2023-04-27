# OPENCORE - ADD
import datetime


class Stats():

	@staticmethod
	def fill_missing_dates(date_from, 
						   date_to, 
						   known_dates_list: list):

		"""
		date_from, a python datetime.datetime object

		"""

		# CAREFUL
		# ASSUMES *assending* ORDERED!!!!! (

		with_missing_dates = []

		if isinstance(date_from, datetime.datetime) is False:
			date_from = datetime.datetime.strptime(date_from,  "%Y-%m-%d")
			date_to = datetime.datetime.strptime(date_to,  "%Y-%m-%d")
		
		next_date = date_from

		period_desired = (date_to - date_from).days
	
		len_period = len(known_dates_list)

		known_date_index = 0
		for i in range(period_desired):

			# date() "Return date object with same year, month and day."

			if known_date_index + 1 <= len_period:
				known_date = known_dates_list[known_date_index]
				if known_date.date() == next_date.date()	:			
				    with_missing_dates.append(known_date) 
				    known_date_index += 1
				else:
				    with_missing_dates.append(next_date)
			else:			
				with_missing_dates.append(next_date)
				
			next_date = next_date + datetime.timedelta(days=1)

		return with_missing_dates