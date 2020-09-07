#!/usr/bin/python
from configparser import ConfigParser


def config(filename='ini/pr_database.ini', section='postgres'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgres
    params = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            params[item[0]] = item[1]

    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return params
