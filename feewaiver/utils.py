import sys
import pytz
from django.db import connection
import os
import subprocess
from pathlib import Path


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


def get_git_commit_hash(repo_path: Path):
    """
    Attempts to get the latest Git commit hash from a given repository path.
    Returns the hash string if successful, otherwise returns None.
    
    :param repo_path: The Path object to the root of the repository.
    """
    # repo_path might be 'str'.  Convert it to the Path obj.
    repo_path = Path(repo_path)

    # The .git directory should be directly inside the repo_path
    git_dir = repo_path / '.git'
    if not os.path.isdir(git_dir):
        return None

    try:
        # Run the git command using the provided path as the working directory.
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%H'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Handle cases where git command fails or is not found.
        return None

