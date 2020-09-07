#!/usr/bin/env python3

import sys

sys.path.append("..")

from config import config

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

CONFIG_FILE = '../ini/pr_database.ini'
CONFIG_SECTION = 'postgres'

params = config(filename=CONFIG_FILE, section=CONFIG_SECTION)

POSTGRES_ENGINE = 'postgres://' + params['user'] + ':' + params['password'] \
                  + '@' + params['host'] + ':' + params['port'] \
                  + '/' + params['database']

engine = create_engine(POSTGRES_ENGINE)
Session = sessionmaker(bind=engine)

session = Session()

try:
    #sql = 'select version();'
    result = session.execute('SELECT * from fabric_people;')
    op = (row[0] for row in result)
    print(op)
except Exception as e:
    # e holds description of the error
    error_text = "<p>The error:<br>" + str(e) + "</p>"
    hed = '<h1>Something is broken.</h1>'
    print(hed + error_text)

session.close()
