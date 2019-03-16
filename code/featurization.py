import sys

import dask
import dask.distributed
import numpy as np
import pandas as pd
import scipy.sparse as sparse
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import pickle

import conf


client = dask.distributed.Client('localhost:8786')
np.set_printoptions(suppress=True)
TRAIN_INPUT = conf.train_tsv
TEST_INPUT = conf.test_tsv
TRAIN_OUTPUT = conf.train_matrix
TEST_OUTPUT = conf.test_matrix


@dask.delayed
def workflow(train_input, test_input, train_output, test_output):
    def get_df(input):
        df = pd.read_csv(
            input,
            encoding='utf-8',
            header=None,
            delimiter='\t',
            names=['id', 'label', 'text']
        )
        sys.stderr.write('The input data frame {} size is {}\n'.format(
            input, df.shape))
        return df

    def save_matrix(df, matrix, output):
        id_matrix = sparse.csr_matrix(df.id.astype(np.int64)).T
        label_matrix = sparse.csr_matrix(df.label.astype(np.int64)).T

        result = sparse.hstack([id_matrix, label_matrix, matrix], format='csr')

        msg = 'The output matrix {} size is {} and data type is {}\n'
        sys.stderr.write(msg.format(output, result.shape, result.dtype))

        with open(output, 'wb') as fd:
            pickle.dump(result, fd, pickle.HIGHEST_PROTOCOL)
        pass

    df_train = get_df(train_input)
    train_words = np.array(df_train.text.str.lower().values.astype('U'))

    bag_of_words = CountVectorizer(
        stop_words='english', max_features=5000)
    bag_of_words.fit(train_words)
    train_words_binary_matrix = bag_of_words.transform(train_words)

    tfidf = TfidfTransformer(smooth_idf=False)
    tfidf.fit(train_words_binary_matrix)
    train_words_tfidf_matrix = tfidf.transform(train_words_binary_matrix)

    save_matrix(df_train, train_words_tfidf_matrix, train_output)
    del df_train

    df_test = get_df(test_input)
    test_words = np.array(df_test.text.str.lower().values.astype('U'))
    test_words_binary_matrix = bag_of_words.transform(test_words)
    test_words_tfidf_matrix = tfidf.transform(test_words_binary_matrix)

    save_matrix(df_test, test_words_tfidf_matrix, test_output)


workflow(TRAIN_INPUT, TEST_INPUT, TRAIN_OUTPUT, TEST_OUTPUT).compute()
