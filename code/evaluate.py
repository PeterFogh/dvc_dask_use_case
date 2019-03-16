import dask
import dask.distributed
import sklearn.metrics as metrics
from sklearn.metrics import precision_recall_curve
import pickle

import conf

client = dask.distributed.Client('localhost:8786')
MODEL_FILE = conf.model
TEST_MATRIX_FILE = conf.test_matrix
METRICS_FILE = conf.metrics_file


@dask.delayed
def workflow(model_file, test_matrix_file):
    with open(model_file, 'rb') as fd:
        model = pickle.load(fd)

    with open(test_matrix_file, 'rb') as fd:
        matrix = pickle.load(fd)

    labels = matrix[:, 1].toarray()
    x = matrix[:, 2:]

    predictions_by_class = model.predict_proba(x)
    predictions = predictions_by_class[:, 1]

    precision, recall, thresholds = precision_recall_curve(labels, predictions)

    auc = metrics.auc(recall, precision)
    return auc


auc = workflow(MODEL_FILE, TEST_MATRIX_FILE).compute()

print('AUC={}'.format(auc))
with open(METRICS_FILE, 'w') as fd:
    fd.write('AUC: {:4f}\n'.format(auc))
