import sys
import pytz
from django.db import connection


def to_local_tz(time_zone, _date):
    local_tz = pytz.timezone(time_zone)
    return _date.astimezone(local_tz)

def check_db_connection():
    """  check connection to DB exists, connect if no connection exists """
    try:
        if not connection.is_usable():
            connection.connect()
    except Exception as e:
        connection.connect()

def are_migrations_running():
    '''
    Checks whether the app was launched with the migration-specific params
    '''
    # return sys.argv and ('migrate' in sys.argv or 'makemigrations' in sys.argv)
    return sys.argv and ('migrate' in sys.argv or 'makemigrations' in sys.argv or 'showmigrations' in sys.argv or 'sqlmigrate' in sys.argv)

