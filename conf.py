"""
Define paths to all DVC dependency and output files.

"""
from pathlib import Path
from urllib.parse import urlparse

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
