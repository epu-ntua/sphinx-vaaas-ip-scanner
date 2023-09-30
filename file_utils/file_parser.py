import yaml
import glob
import os
import json
import logging
from utils.utils import *

l = get_main_logger('file_parser.py')


def read_file(path):
    try:
        with open(path, mode='r') as f:
            return json.loads(f.read())
    except Exception as e:
        l.exception(dmsg('') + e.__str__())


def get_files(_dir='scan_results', file='*.json'):
    try:
        scan_results = []
        path = str(os.path.join(str(get_project_root()), 'scan_results', file))
        for filepath in glob.iglob(path, recursive=True):
            # print(filepath)
            # print(read_file(filepath))
            l.debug(f'Traversing path: {filepath} to parse scan results...')
            scan_results.append({os.path.basename(filepath).replace('.json', ''): read_file(filepath)})
        if scan_results:
            l.info(dmsg('') + ' Successfully loaded/parsed discovered entities files.')
            # print(scan_results)
            return scan_results
        else:
            l.error(dmsg('') + ' Did NOT find any scan results!!')
    except Exception as e:
        l.exception(e.__str__())
        return []




def parseYaml(path):
    with open(path) as stream:
        try:
            file = yaml.safe_load(stream)
            # l.debug(dmsg('') + f' parsed file {file}')
            return file
        except yaml.YAMLError as e:
            l.exception(e.__str__())
            return None


# print(get_files())
