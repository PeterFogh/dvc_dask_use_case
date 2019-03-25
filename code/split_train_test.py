"""
Split the dataset into train and test set.

Routine Listings
----------------
get_params()
    Get the DVC stage parameters.
split(seed, test_ratio, input_path, train, test)
    Split dataset into train and test set.

"""
import sys

import dask
import dask.distributed
import pandas as pd
from sklearn.model_selection import train_test_split

import conf


def get_params():
    """Get the DVC stage parameters."""
    return {
        'test_ratio': 0.33,
        'seed': 42}


@dask.delayed
def split(seed, test_ratio, input_path, train, test):
    """Split dataset into train and test set."""
    def sub_df_by_ids(df, ids):
        df_train_order = pd.DataFrame(data={'id': ids})
        return df.merge(df_train_order, on='id')

    def train_test_split_df(df, ids, test_ratio, seed):
        train_ids, test_ids = train_test_split(
            ids, test_size=test_ratio, random_state=seed)
        return sub_df_by_ids(df, train_ids), sub_df_by_ids(df, test_ids)

    df = pd.read_csv(
        input_path,
        encoding='utf-8',
        header=None,
        delimiter='\t',
        names=['id', 'label', 'text']
    )

    df_positive = df[df['label'] == 1]
    df_negative = df[df['label'] == 0]

    sys.stderr.write('Positive size {}, negative size {}\n'.format(
        df_positive.shape[0],
        df_negative.shape[0]
    ))

    df_pos_train, df_pos_test = train_test_split_df(
        df, df_positive.id, test_ratio, seed)
    df_neg_train, df_neg_test = train_test_split_df(
        df, df_negative.id, test_ratio, seed)

    df_train = pd.concat([df_pos_train, df_neg_train])
    df_test = pd.concat([df_pos_test, df_neg_test])

    df_train.to_csv(train, sep='\t', header=False, index=False)
    df_test.to_csv(test, sep='\t', header=False, index=False)


if __name__ == '__main__':
    client = dask.distributed.Client('localhost:8786')
    INPUT_PATH = conf.source_tsv
    TRAIN = conf.train_tsv
    TEST = conf.test_tsv

    config = get_params()
    TEST_RATIO = config['test_ratio']
    SEED = config['seed']

    split(SEED, TEST_RATIO, INPUT_PATH, TRAIN, TEST).compute()
