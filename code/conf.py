"""
Define paths to all DVC dependency and output files.

"""
import os
from pathlib import Path
from urllib.parse import urlparse

from dvc.repo import Repo
dvc_repo = Repo('.')
# Specify the name of your DVC remote
DVC_REMOTE_NAME = 'ahsoka'
# Specify the name of your remote DVC data directory for this project
PROJECT_NAME = 'dvc_dask_use_case'

# Get DVC remote URL to your remote work directory
remote_work_path = urlparse(
    dvc_repo.config.config[f'remote "{DVC_REMOTE_NAME}"']['url']).path
remote_work_path = Path(remote_work_path)

# Specify the paths to the DVC stage dependencies and ourputs
data_dir = remote_work_path/PROJECT_NAME/'data'

source_xml = os.path.join(data_dir, 'Posts.xml')
source_tsv = os.path.join(data_dir, 'Posts.tsv')

train_tsv = os.path.join(data_dir, 'Posts-train.tsv')
test_tsv = os.path.join(data_dir, 'Posts-test.tsv')

train_matrix = os.path.join(data_dir, 'matrix-train.p')
test_matrix = os.path.join(data_dir, 'matrix-test.p')

model = os.path.join(data_dir, 'model.p')

metrics_file = 'eval.txt'
