#!/usr/bin/env python3
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append("..")
from config import config

# Setup database engine
CONFIG_FILE = '../ini/pr_database.ini'
CONFIG_SECTION = 'postgres'

params = config(filename=CONFIG_FILE, section=CONFIG_SECTION)

POSTGRES_ENGINE = 'postgres://' + params['user'] + ':' + params['password'] \
                  + '@' + params['host'] + ':' + params['port'] \
                  + '/' + params['database']

engine = create_engine(POSTGRES_ENGINE)
Session = sessionmaker(bind=engine)

# Setup COmanage LDAP connection
CONFIG_FILE = '../ini/pr_comanage.ini'
CONFIG_SECTION = 'ldap'

LDAP_PARAMS = config(filename=CONFIG_FILE, section=CONFIG_SECTION)
