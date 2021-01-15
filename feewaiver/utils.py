import requests
import sys
import json
from datetime import timedelta, date, datetime
import pytz
from django.conf import settings
from django.core.cache import cache
from django.db import connection


def to_local_tz(_date):
    local_tz = pytz.timezone(settings.TIME_ZONE)
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

