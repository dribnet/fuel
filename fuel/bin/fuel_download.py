#!/usr/bin/env python
"""Fuel dataset downloading utility."""
import argparse
import importlib
import os
import sys

import fuel
from fuel import downloaders
from fuel.downloaders.base import NeedURLPrefix
from fuel.utils import import_function_by_name

url_prefix_message = """
Some files for this dataset do not have a download URL.

Provide a URL prefix with --url-prefix to prepend to the filenames,
e.g. http://path.to/files/
""".strip()

def update_datasets(built_in_datasets, name):
    """Add packages to list of built in datasets by name"""
    extra_datasets = dict(importlib.import_module(name).all_downloaders)
    if any(key in built_in_datasets for key in extra_datasets.keys()):
        raise ValueError('extra downloaders conflict in name with '
                         'built-in downloaders')
    built_in_datasets.update(extra_datasets)

def handle_extra(built_in_datasets):
    """Special pre-parser for --extra"""
    if "--extra" in sys.argv:
        ix = sys.argv.index("--extra")
        if ix > len(sys.argv) - 2:
            return
        update_datasets(built_in_datasets, sys.argv[ix+1])
        sys.argv[ix:ix+2] = []

def main(args=None):
    """Entry point for `fuel-download` script.

    This function can also be imported and used from Python.

    Parameters
    ----------
    args : iterable, optional (default: None)
        A list of arguments that will be passed to Fuel's downloading
        utility. If this argument is not specified, `sys.argv[1:]` will
        be used.

    """

    built_in_datasets = dict(downloaders.all_downloaders)
    if fuel.config.extra_downloaders:
        for name in fuel.config.extra_downloaders:
            update_datasets(built_in_datasets, name)
    handle_extra(built_in_datasets)
    parser = argparse.ArgumentParser(
        description='Download script for built-in datasets.')
    parser.add_argument(
        "--extra", help="add an extra downloader package",
        type=str, default=None)
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-d", "--directory", help="where to save the downloaded files",
        type=str, default=os.getcwd())
    parent_parser.add_argument(
        "--clear", help="clear the downloaded files", action='store_true')
    subparsers = parser.add_subparsers()
    for name, subparser_fn in built_in_datasets.items():
        subparser_fn(subparsers.add_parser(
            name, parents=[parent_parser],
            help='Download the {} dataset'.format(name)))
    args = parser.parse_args()
    args_dict = vars(args)
    args_dict.pop("extra", None)
    try:
        func = import_function_by_name(args_dict.pop('func'))
    except KeyError:
        parser.print_usage()
        parser.exit()
    try:
        func(**args_dict)
    except NeedURLPrefix:
        parser.error(url_prefix_message)


if __name__ == "__main__":
    main()
