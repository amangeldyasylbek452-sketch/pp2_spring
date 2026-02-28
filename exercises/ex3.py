#program to subtract five days from current date.

from datetime import datetime, timedelta

current_date = datetime.now()
print("Current date:", current_date)
new_date = current_date - timedelta(days=5)
print("Date after subtracting five days:", new_date)



#program to print yesterday, today, tomorrow.

from datetime import datetime, timedelta

current_date = datetime.now()
print("Today:", current_date)
yesterday = current_date - timedelta(days=1)
print("Yesterday:", yesterday)
tomorrow = current_date + timedelta(days=1)
print("Tomorrow:", tomorrow)



#program to drop microseconds from datetime

from datetime import datetime

current_date = datetime.now()
print("Current date and time:", current_date)
new_date = current_date.replace(microsecond=0)
print("Date and time without microseconds:", new_date)



#program to calculate two date difference in seconds.

from datetime import datetime

date1 = datetime(2024, 6, 1, 12, 0, 0)
date2 = datetime(2024, 6, 2, 12, 0, 0)
difference = date2 - date1
print("Difference in seconds:", difference.total_seconds())
