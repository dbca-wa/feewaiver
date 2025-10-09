import sys
import pytz
from django.db import connection
import time
from pathlib import Path
from typing import Union


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


def get_git_commit_hash(base_dir: Union[str, Path]):
    """
    Reads the git commit hash from a file generated during the Docker build.
    Provides a fallback to the current timestamp for local development
    environments where the file may not exist.
    
    :param base_dir: A Path object to the project's base directory.
    """
    try:
        # Define the path to the hash file relative to the base directory.
        base_dir = Path(base_dir)
        hash_file_path = base_dir / 'GIT_COMMIT_HASH.txt'
        
        # Open the file, read its content, and strip any surrounding whitespace.
        with open(hash_file_path, 'r') as f:
            hash_value = f.read().strip()
            # Ensure the file is not empty. If it is, fall back.
            if hash_value:
                return hash_value
        
        # If the file exists but is empty, manually raise an error to trigger the except block.
        raise FileNotFoundError

    except FileNotFoundError:
        # If the file is not found (e.g., in local development),
        # return the current Unix timestamp as a string for cache busting.
        return str(int(time.time()))