import sys

import dask
import dask.distributed
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle

import conf


client = dask.distributed.Client('localhost:8786')
INPUT = conf.train_matrix
OUTPUT = conf.model


@dask.delayed
def workflow(input, output, seed):

    with open(input, 'rb') as fd:
        matrix = pickle.load(fd)

    labels = np.squeeze(matrix[:, 1].toarray())
    x = matrix[:, 2:]

    sys.stderr.write('Input matrix size {}\n'.format(matrix.shape))
    sys.stderr.write('X matrix size {}\n'.format(x.shape))
    sys.stderr.write('Y matrix size {}\n'.format(labels.shape))

    clf = RandomForestClassifier(n_estimators=100, n_jobs=2, random_state=seed)
    clf.fit(x, labels)

    with open(output, 'wb') as fd:
        pickle.dump(clf, fd)


if len(sys.argv) != 2:
    sys.stderr.write('Arguments error. Usage:\n')
    sys.stderr.write(
        '\tpython train_model.py INPUT_MATRIX_FILE SEED OUTPUT_MODEL_FILE\n')
    sys.exit(1)

seed = int(sys.argv[1])

workflow(INPUT, OUTPUT, seed).compute()
