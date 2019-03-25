"""
Transform XML data file to a TSV file.

Routine Listings
----------------
get_params()
    Get the DVC stage parameters.
process_xml_to_tsv(input_path, output_path)
    Load and process XML file and save the data to TSV file.

"""
import sys
import os

import dask
import dask.distributed
import xml.etree.ElementTree

import conf


def get_params():
    """Get the DVC stage parameters."""
    return {}


@dask.delayed
def process_xml_to_tsv(input_path, output_path):
    """Load and process XML file and save the data to TSV file."""
    TAG = 'python'
    target_tag = u'<' + TAG + '>'

    if not os.path.exists(input_path):
        sys.stderr.write(f'Input file {input_path} does not exist')
        sys.stderr.write('Usage:\n')
        sys.stderr.write('\tpython posts_to_tsv.py\n')
        sys.exit(1)

    with open(input_path) as fd_in:
        with open(output_path, 'w') as fd_out:
            num = 1
            for line in fd_in:
                try:
                    attr = xml.etree.ElementTree.fromstring(line).attrib

                    id = attr.get('Id', '')
                    label = 1 if target_tag in attr.get('Tags', '') else 0
                    title = attr.get('Title', '').replace('\t', ' ').replace(
                        '\n', ' ').replace('\r', ' ')
                    body = attr.get('Body', '').replace('\t', ' ').replace(
                        '\n', ' ').replace('\r', ' ')
                    text = title + ' ' + body

                    fd_out.write(u'{}\t{}\t{}\n'.format(id, label, text))

                    num += 1
                except Exception as ex:
                    sys.stderr.write('Error in line {}: {}\n'.format(num, ex))


if __name__ == '__main__':
    client = dask.distributed.Client('localhost:8786')

    INPUT = conf.source_xml
    OUTPUT = conf.source_tsv

    process_xml_to_tsv(INPUT, OUTPUT).compute()
