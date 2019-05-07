"""
Train the model.

Routine Listings
----------------
get_params()
    Get the DVC stage parameters.
train(input, output, model, model_params)
    Train model on feature matrix.

"""
import sys

import dask
import dask.distributed
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle

import conf


def get_params():
    """Get the DVC stage parameters."""
    return {
        'classifier': RandomForestClassifier,
        'n_estimators': 100,
        'n_jobs': 2,
        'random_state': 42}


@dask.delayed
def train(input, output, model, model_params):
    """Train model on feature matrix."""
    with open(input, 'rb') as fd:
        matrix = pickle.load(fd)

    labels = np.squeeze(matrix[:, 1].toarray())
    x = matrix[:, 2:]

    sys.stderr.write('Input matrix size {}\n'.format(matrix.shape))
    sys.stderr.write('X matrix size {}\n'.format(x.shape))
    sys.stderr.write('Y matrix size {}\n'.format(labels.shape))

    clf = model(**model_params)
    clf.fit(x, labels)

    with open(output, 'wb') as fd:
        pickle.dump(clf, fd)


if __name__ == '__main__':
    client = dask.distributed.Client('localhost:8786')
    INPUT_TRAIN_MATRIX_PATH = conf.data_dir/'featurization'/'matrix-train.p'
    dvc_stage_name = __file__.strip('.py')
    STAGE_OUTPUT_PATH = conf.data_dir/dvc_stage_name
    conf.remote_mkdir(STAGE_OUTPUT_PATH).compute()
    OUTPUT_MODEL_PATH = STAGE_OUTPUT_PATH/'model.p'

    config = get_params()
    CLASSIFIER = config['classifier']
    N_ESTIMATORS = config['n_estimators']
    N_JOBS = config['n_jobs']
    RANDOM_STATE = config['random_state']

    train(INPUT_TRAIN_MATRIX_PATH, OUTPUT_MODEL_PATH, CLASSIFIER,
          {'n_estimators': N_ESTIMATORS, 'n_jobs': N_JOBS,
           'random_state': RANDOM_STATE}).compute()
