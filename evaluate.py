"""
Compute model performance on test set and save results to `mlflow`.

"""
import dask
import dask.distributed
import mlflow
import pickle
import sklearn.metrics as metrics
from sklearn.metrics import precision_recall_curve

import conf
import featurization
import split_train_test
import train_model
import xml_to_tsv


@dask.delayed
def evaluate(model_file, test_matrix_file):
    """Return AUC for text dataset"""
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


if __name__ == '__main__':
    client = dask.distributed.Client('localhost:8786')
    MODEL_FILE = conf.model
    TEST_MATRIX_FILE = conf.test_matrix
    METRICS_FILE = conf.metrics_file

    auc = evaluate(MODEL_FILE, TEST_MATRIX_FILE).compute()

    print('AUC={}'.format(auc))
    with open(METRICS_FILE, 'w') as fd:
        fd.write('AUC: {:4f}\n'.format(auc))

    CONFIGURATIONS = {
        'xml_to_tsv': xml_to_tsv.get_params(),
        'split_train_test': split_train_test.get_params(),
        'featurization': featurization.get_params(),
        'train_model': train_model.get_params()
    }

    with mlflow.start_run():
        for stage, params in CONFIGURATIONS.items():
            for param, value in CONFIGURATIONS.items():
                mlflow.log_param(param, value)

        mlflow.log_metric("AUC", auc)
