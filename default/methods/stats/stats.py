# OPENCORE - ADD
import datetime


class Stats():

    @staticmethod
    def fill_missing_dates(date_from, 
                           date_to, 
                           known_dates_list: list):
        """
        Fills in missing dates between `date_from` and `date_to` in a list of dates.

        Parameters:
        date_from (datetime.datetime): The start date of the period to fill.
        date_to (datetime.datetime): The end date of the period to fill.
        known_dates_list (list): A list of datetime.datetime objects representing
                                 the known dates within the period.

        Returns:
        list: A new list of datetime.datetime objects with missing dates filled
              between `date_from` and `date_to`.
        """

        # CAREFUL
        # ASSUMES *assending* ORDERED!!!!! (

        with_missing_dates = []

        # Convert input strings to datetime objects if necessary
        if isinstance(date_from, datetime.datetime) is False:
            date_from = datetime.datetime.strptime(date_from,  "%Y-%m-%d")
            date_to = datetime.datetime.strptime(date_to,  "%Y-%m-%d")

        next_date = date_from

        period_desired = (date_to - date_from).days

        len_period = len(known_dates_list)

        known_date_index = 0
        for i in range(period_desired):

            # Check if the next date in the sequence is a known date
            if known_date_index + 1 <= len_period:
                known_date = known_dates_list[known_date_index]
                if known_date.date() == next_date.date():
                    with_missing_dates.append(known_date) 
                    known_date_index += 1
                else:
                    # Add a missing date to the sequence
                    with_missing_dates.append(next_date)
            else:
                # Add a missing date to the sequence
                with_missing_dates.append(next_date)

            # Increment the next date in the sequence
            next_date = next_date + datetime.timedelta(days=1)

        return with_missing_dates
