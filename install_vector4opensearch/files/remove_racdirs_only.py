#!/usr/bin/env python3

import os
import shutil
import argparse

# Рекурсивно удалить папки, начинающиеся с 'rac_' в заданной директории
def remove_rac_directories(directory):
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            if dir_name.startswith('rac_'):
                dir_path = os.path.join(root, dir_name)
                shutil.rmtree(dir_path)

def main(args):
    directories = args.directory
    for dir in directories:
        remove_rac_directories(dir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', required=False, default=["/var/1C"], 
                        help="Путь к директориям, в которых нужно удалить папки 'rac_*'")
    args = parser.parse_args()
    main(args)
