# DVC and Dask use case

This repository contains the description and code for setting up [DVC](https://dvc.org/) to use a remote computer server using [dask](https://docs.dask.org/en/latest/). Note that this use case relay on the original DVC tutorial and its code found here https://dvc.org/doc/tutorial.

## How to set up the use case

### Prerequisites

The use case have the following prerequisites:

1. A remote server with:
    1. SSH installed.
    1. A unix user you have the username and password for.
    1. A folder for your remote shared DVC cache, my is at `/scratch/dvc_data_cache/`.
    1. A folder for your remote DVC data directories, my is at `/scratch/dvc_users/[REMOTE_USERNAME]/`.
    1. A Dask scheduler installed and running at port 8786, see http://docs.dask.org/en/latest/setup.html for a guide.
    1. A MLflow tracking server installed and running at host 0.0.0.0 and port 5000, with `mlflow server --host 0.0.0.0 --file-store /projects/mlflow_runs/`.
1. A local SSH keyfile (`ssh-keygen`), which have been copied to the remote server: `ssh-copy-id [REMOTE_USERNAME]@[REMOTE_IP]`.
1. An open SSH port-forward to the Dask scheduler and MLflow tracking server from your local machine to the remote server, with `ssh -L 8786:[REMOTE_USERNAME]@[REMOTE_IP]:8786, -L 5000:[REMOTE_USERNAME]@[REMOTE_IP]:5000 [REMOTE_USERNAME]@[REMOTE_IP]`.
1. Set up local DVC development repository (following https://dvc.org/doc/user-guide/contributing/) with a conda environment:
    1. Fork https://github.com/iterative/dvc on Github.
    1. `git clone git@github.com:<GITHUB_USERNAME>/dvc.git`
    1. `cd dvc`
    1. `conda create -n py36_open_source_dvc python=3.6`
    1. `conda activate py36_open_source_dvc`
    1. `pip install -r requirements.txt`
    1. `pip install -r tests/requirements.txt`
    1. `pip install -e .`
    1. `pip install pre-commit`
    1. `pre-commit install`
    1. `which dvc` should say `[HOME]/anaconda3/envs/py36_open_source_dvc/bin/dvc` and `dvc --version` should say the exact version available in you local DVC development repository.
1. Configure you local DVC globally for you local machine, note that I call my remote server "ahsoka":
    1. `conda activate py36_open_source_dvc`
    1. `dvc remote add ahsoka ssh://[REMOTE_IP]/scratch/dvc_users/[REMOTE_USERNAME]/ --global`
    1. `dvc remote modify ahsoka user [REMOTE_USERNAME] --global`
    1. `dvc remote modify ahsoka port 22 --global`
    1. `dvc remote modify ahsoka keyfile [PATH_TO_YOUR_PUBLIC_SSH_KEY] --global`
    1. `dvc remote add ahsoka_cache ssh://[REMOTE_IP]/scratch/dvc_data_cache --global`
    1. `dvc remote modify ahsoka_cache user [REMOTE_USERNAME] --global`
    1. `dvc remote modify ahsoka_cache port 22 --global`
    1. `dvc remote modify ahsoka_cache keyfile [PATH_TO_YOUR_PUBLIC_SSH_KEY] --global`
    1. `dvc config cache.ssh ahsoka_cache --global`

## Use case

This use case of DVC and Dask has been set up as follow.

On your remote server do the following:

1. To create the remote DVC data directory for this project (i.e. this use case):
    1. `cd scratch/dvc_users/[REMOTE_USERNAME]`
    1. `mkdir dvc_dask_use_case`
    1. `cd dvc_dask_use_case`
    1. `wget -P ./ https://s3-us-west-2.amazonaws.com/dvc-share/so/100K/Posts.xml.tgz`
    1. `tar zxf ./Posts.xml.tgz -C ./`

On your local machine do the following:

1. Clone this test repository from my Github: `git clone git@github.com:PeterFogh/dvc_dask_use_case.git`
1. Install the Conda environment for this repository - note the new enviroment must point to your local DVC development repository:
    1. `conda env create -f conda_env.yml`, which have been create by the following commands (executed the 16-03-2019):
        1. `conda create --name py36_open_source_dvc_dask_use_case --clone py36_open_source_dvc`
        1. `conda install -n py36_open_source_dvc_dask_use_case dask scikit-learn`
        1. `pip install mlflow matplotlib`
        1. `conda env export -n py36_open_source_dvc_dask_use_case > conda_env.yml`
    1. Check dvc version matches your development repository version: `conda activate py36_open_source_dvc && which dvc && dvc --version` and ``conda activate py36_open_source_dvc_dask_use_case && which dvc && dvc --version``
1. Reproduce the DVC pipeline: `dvc repro` - which have been specified by the following DVC stages:
    1. `conda activate py36_open_source_dvc_dask_use_case`
    1. `dvc run -d xml_to_tsv.py -d conf.py -d remote://ahsoka/dvc_dask_use_case/Posts.xml -o remote://ahsoka/dvc_dask_use_case/Posts.tsv -f xml_to_tsv.dvc python xml_to_tsv.py`
    1. `dvc run -d split_train_test.py -d conf.py -d remote://ahsoka/dvc_dask_use_case/Posts.tsv -o remote://ahsoka/dvc_dask_use_case/Posts-test.tsv -o remote://ahsoka/dvc_dask_use_case/Posts-train.tsv -f split_train_test.dvc python split_train_test.py`
    1. `dvc run -d featurization.py -d conf.py -d remote://ahsoka/dvc_dask_use_case/Posts-train.tsv -d remote://ahsoka/dvc_dask_use_case/Posts-test.tsv -o remote://ahsoka/dvc_dask_use_case/matrix-train.p -o remote://ahsoka/dvc_dask_use_case/matrix-test.p -f featurization.dvc python featurization.py`
    1. `dvc run -d train_model.py -d conf.py -d remote://ahsoka/dvc_dask_use_case/matrix-train.p -o remote://ahsoka/dvc_dask_use_case/model.p -f train_model.dvc python train_model.py`
    1. `dvc run -d evaluate.py -d conf.py -d remote://ahsoka/dvc_dask_use_case/model.p -d remote://ahsoka/dvc_dask_use_case/matrix-test.p -m eval.txt -f Dvcfile python evaluate.py`
1. Show DVC metrics `dvc metrics show -a`.
1. Visit MLflow tracking server webUI from your local browser at http://localhost:5000/ to see the results of the pipeline.

## Problems with MLflow for the use case

- **MLflow artifacts do not support our SSH setup.** `mlflow.log_artifacts()` do not support files saved on the remote server. Artifact files must be located at a directory shared by both the client machine and the server using the methods [described here](https://www.mlflow.org/docs/latest/tracking.html#supported-artifact-stores). Read https://github.com/mlflow/mlflow/issues/572#issuecomment-427718078 for more details on the problem. **However, we can circumvent this problem using Dask to executed the MLflow run on the remote server. Thereby, both the client and the MLflow tracking server has not problem reading and writing to the same folder, as the they are executed on the same machine.**  
