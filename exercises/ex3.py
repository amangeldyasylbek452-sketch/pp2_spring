#program to subtract five days from current date.
from datetime import datetime, timedelta
current_date = datetime.now()
print("Current date:", current_date)
new_date = current_date - timedelta(days=5)
print("Date after subtracting five days:", new_date)
