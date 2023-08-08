import os


dbname = os.environ.get('DBNAME')
dbuser = os.environ.get('DBUSER')
dbpass = os.environ.get('DBPASS')


class DBConfig:
    params = {
        'host': 'localhost',
        'dbname': dbname,
        'user': dbuser,
        'password': dbpass,
    }