"""
Download XML data.

Routine Listings
----------------
get_params()
    Get the DVC stage parameters.
process_xml_to_tsv(input_path, output_path)
    Load and process XML file and save the data to TSV file.

"""
import tarfile

import dask
import dask.distributed
import requests

import conf


def get_params():
    """Get the DVC stage parameters."""
    return {}


@dask.delayed
def download_xml(output_folder_path):
    """Download XML data file."""
    url = 'https://s3-us-west-2.amazonaws.com/dvc-share/so/100K/Posts.xml.tgz'
    r = requests.get(url=url, stream=True)
    tgz_file_path = output_folder_path/url.split('/')[-1]
    if r.status_code == 200:
        with open(tgz_file_path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)

    tf = tarfile.open(tgz_file_path)
    tf.extractall(path=output_folder_path)


if __name__ == '__main__':
    client = dask.distributed.Client('localhost:8786')
    dvc_stage_name = __file__.strip('.py')
    STAGE_OUTPUT_PATH = conf.data_dir/dvc_stage_name
    conf.remote_mkdir(STAGE_OUTPUT_PATH).compute()
    OUTPUT_DATASET_TSV_PATH = STAGE_OUTPUT_PATH/'Posts.xml'

    download_xml(STAGE_OUTPUT_PATH).compute()
