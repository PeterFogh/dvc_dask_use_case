"""
Define paths to all DVC dependency and output files.

"""
from pathlib import Path
from urllib.parse import urlparse

import dask
from dvc.repo import Repo
dvc_repo = Repo('.')

# Get DVC remote URL to your remote work directory for this project
remote_user_work_path = urlparse(
    dvc_repo.config.config[f'remote "ahsoka_user_workspace"']['url']).path
remote_user_work_path = Path(remote_user_work_path)
remote_project_work_path = urlparse(
    dvc_repo.config.config[f'remote "ahsoka_project_data"']['url']).path
remote_project_work_folder_name = Path(remote_project_work_path).name
remote_work_path = remote_user_work_path/remote_project_work_folder_name

# Get DVC remote URL to the project cache
remote_cache_path = urlparse(
    dvc_repo.config.config[f'remote "ahsoka_project_cache"']['url']).path
remote_cache_path = Path(remote_cache_path)

assert remote_work_path.name == remote_cache_path.name, (
    'The name of your remote DVC data directory for this project:'
    f'"{remote_work_path.name}", is should be the same as the same as the name'
    f'of the project cache directory: "{remote_cache_path.name}')

data_dir = remote_work_path


@dask.delayed
def remote_mkdir(folder_path):
    """
    Create the given folder on the remote server with the correct permissions.

    Create a folder on the remote dask worker server. The mode and permissions
    of the folder is set to "2770". The SGID "2" ensures that new files in the
    folder will be create with the same group permissions as the folder itself.
    The umask "770" ensures that both the user and the group members have read,
    write, and execute permissions to the folder and its files, where as all
    other user have no permissions.

    Parameters
    ----------
    folder_path : pathlib.Path
        Path to the folder you wishes to create with the correct permissions.

    Returns
    -------
    folder : pathlib.Path
        Path to the folder which have been create with the correct permissions,
        if the folder already existed we assume it has the correct permissions
        as we may do not have permissions to change its permissions.

    """
    if not folder_path.exists():
        folder_path.mkdir()
        folder_path.chmod(mode=0o2770)

    return folder_path
