import datetime


entry = '2023-07-27T14:12:25+02:00'
date_time = datetime.datetime.strptime(entry, '%Y-%m-%dT%H:%M:%S+02:00')
print(date_time.day == 27)
