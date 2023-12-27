import re
from importlib import import_module
from os.path import *
import shutil
import os
import inspect

import yaml
from hstest import StageTest


def get_if_statement(code):
    pattern = r"if __name__ == [\"']__main__[\"']:[\s\w\W]+"
    result = re.findall(pattern, code)
    return result[-1]


def handle_stage(stage_dir):
    test_folder = join(stage_dir, 'test')
    if not exists(test_folder):
        os.mkdir(test_folder)
    open(join(test_folder, '__init__.py'), 'a').close()
    test_file_path = os.path.join(stage_dir, 'tests.py')
    test_file_new_path = os.path.join(stage_dir, 'test', 'tests.py')
    shutil.copy(test_file_path, test_file_new_path)
    imported = import_module('stage1.test.tests')
    test_class_name = None
    for name, obj in inspect.getmembers(imported):
        if inspect.isclass(obj) and issubclass(obj, StageTest) and obj != StageTest:
            test_class_name = name
            break

    if_statement = get_if_statement(open(test_file_new_path, 'r').read())
    import_statement = f'from test.tests import {test_class_name}'
    with open(test_file_path, 'w') as f:
        f.write(import_statement + '\n\n' + if_statement)

    with open(join(stage_dir, 'task-info.yaml'), 'r') as file:
        task_info = yaml.load(file, Loader=yaml.FullLoader)
        task_info['files'].append({
            'name': 'test/tests.py',
            'visible': False
        })
        task_info['files'].append({
            'name': 'test/__init__.py',
            'visible': False
        })
    with open(join(stage_dir, 'task-info.yaml'), 'w') as file:
        yaml.dump(task_info, file)


for i in range(1, 20):
    if not exists(join(os.getcwd(), f'stage{i}')):
        break
    handle_stage(f'stage{i}')