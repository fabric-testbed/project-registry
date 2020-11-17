#!/usr/bin/env python3
from swagger_server import Session
import psycopg2
import requests
from flask import request
from ..external_apis.uis_api import uis_get_uuid_from_oidc_claim_sub
from . import COOKIE_NAME, COOKIE_DOMAIN


def dict_from_query(query=None):
    session = Session()
    a = None
    try:
        resultproxy = session.execute(query)
        d, a = {}, []
        for rowproxy in resultproxy:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            for column, value in rowproxy.items():
                # build up the dictionary
                d = {**d, **{column: value}}
            a.append(d)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if session is not None:
            session.close()

    return a


def run_sql_commands(commands):
    session = Session()
    try:
        if isinstance(commands, tuple):
            for command in commands:
                session.execute(command)
        else:
            session.execute(commands)
        session.commit()
        print("[INFO] data loaded successfully!")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if session is not None:
            session.close()


def resolve_empty_people_uuid():
    sql = """
    SELECT id, oidc_claim_sub FROM fabric_people
    WHERE uuid = '';
    """
    dfq = dict_from_query(sql)
    if dfq:
        s = requests.Session()
        cookie_value = request.cookies.get(COOKIE_NAME)
        cookie_obj = requests.cookies.create_cookie(
            domain=COOKIE_DOMAIN,
            name=COOKIE_NAME,
            value=cookie_value
        )
        s.cookies.set_cookie(cookie_obj)
        cookies = s.cookies
        sql_list = []
        for person in dfq:
            people_id = person.get('id')
            oidc_claim_sub = person.get('oidc_claim_sub')
            uuid = uis_get_uuid_from_oidc_claim_sub(oidc_claim_sub, cookies)

            sql = """
            UPDATE fabric_people
            SET uuid = '{0}'
            WHERE fabric_people.id = {1};
            """.format(uuid, people_id)
            sql_list.append(sql)

        commands = tuple(i for i in sql_list)
        print("[INFO] attempt to update people uuid data")
        run_sql_commands(commands)
