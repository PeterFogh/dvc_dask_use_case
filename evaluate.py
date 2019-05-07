"""
Compute model performance on test set and save results to MLflow.

Routine Listings
----------------
evaluate()
    Return AUC for text dataset.
save_mlflow_run(params, metrices, artifacts)
    Save MLflow run (params, metrices, artifacts) to tracking server.
save_plot(path, train_auc, test_auc)
    Save plot of train and test AUC to file.

"""
import dask
import dask.distributed
import mlflow
import pandas as pd
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
    """Return AUC for text dataset."""
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


@dask.delayed
def save_mlflow_run(params, metrices, artifacts):
    """Save MLflow run (params, metrices, artifacts) to tracking server."""
    mlflow.set_tracking_uri('http://localhost:5000')
    mlflow.set_experiment('dvc_dask_use_case')
    with mlflow.start_run():
        for stage, stage_params in params.items():
            for key, value in stage_params.items():
                mlflow.log_param(key, value)

        for metric, value in metrices.items():
            mlflow.log_metric(metric, value)

        for path in artifacts:
            mlflow.log_artifact(path)


@dask.delayed
def save_plot(path, train_auc, test_auc):
    """Save plot of train and test AUC to file."""
    data = pd.Series(
        {'train_auc': train_auc, 'test_auc': test_auc})
    ax = data.plot.bar()
    fig = ax.get_figure()
    fig.savefig(path)


if __name__ == '__main__':
    client = dask.distributed.Client('localhost:8786')
    INPUT_TRAIN_MATRIX_PATH = conf.data_dir/'featurization'/'matrix-train.p'
    INPUT_TEST_MATRIX_PATH = conf.data_dir/'featurization'/'matrix-test.p'
    INPUT_MODEL_PATH = conf.data_dir/'train_model'/'model.p'
    dvc_stage_name = __file__.strip('.py')
    STAGE_OUTPUT_PATH = conf.data_dir/dvc_stage_name
    conf.remote_mkdir(STAGE_OUTPUT_PATH).compute()
    OUTPUT_METRICS_PATH = 'eval.txt'
    OUTPUT_PLOT_PATH = STAGE_OUTPUT_PATH/'train_test_auc_plot.png'

    train_auc = evaluate(INPUT_MODEL_PATH, INPUT_TRAIN_MATRIX_PATH).compute()
    test_auc = evaluate(INPUT_MODEL_PATH, INPUT_TEST_MATRIX_PATH).compute()

    save_plot(OUTPUT_PLOT_PATH, train_auc, test_auc).compute()

    print('TRAIN_AUC={}'.format(train_auc))
    print('TEST_AUC={}'.format(test_auc))
    with open(OUTPUT_METRICS_PATH, 'w') as fd:
        fd.write('TRAIN_AUC: {:4f}\n'.format(train_auc))
        fd.write('TEST_AUC: {:4f}\n'.format(test_auc))

    CONFIGURATIONS = {
        'xml_to_tsv': xml_to_tsv.get_params(),
        'split_train_test': split_train_test.get_params(),
        'featurization': featurization.get_params(),
        'train_model': train_model.get_params()
    }

    overall_scores = {
        'TRAIN_AUC': train_auc,
        'TEST_AUC': test_auc
    }

    save_mlflow_run(
        CONFIGURATIONS, overall_scores, [OUTPUT_PLOT_PATH]).compute()
