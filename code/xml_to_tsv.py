import sys
import os
import xml.etree.ElementTree
import conf

import dask
import dask.distributed

client = dask.distributed.Client('localhost:8786')

INPUT = conf.source_xml
OUTPUT = conf.source_tsv


@dask.delayed
def workflow(input_path, output_path):
    def print_usage(msg):
        if msg:
            sys.stderr.write('{}\n'.format(msg))
        sys.stderr.write('Usage:\n')
        sys.stderr.write('\tpython posts_to_tsv.py\n')

    def process_posts(fd_in, fd_out, target_tag):
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

    TAG = 'python'
    target_tag = u'<' + TAG + '>'

    if not os.path.exists(input_path):
        print_usage('Input file {} does not exist'.format(input_path))
        sys.exit(1)

    with open(input_path) as fd_in:
        with open(output_path, 'w') as fd_out:
            process_posts(fd_in, fd_out, target_tag)


if __name__ == '__main__':
    workflow(INPUT, OUTPUT).compute()
