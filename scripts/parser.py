import os
import sys
import json
import uuid
import requests

from functools import wraps
from time import time
import pandas as pd

from clickhouse_driver import Client
from scripts.models import EventsLog, db


def gen_random_text():
    return uuid.uuid4().hex


# Measure time of function work
def timing(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time()
        result = f(*args, **kwargs)
        end = time()
        print('Elapsed time: {}'.format(end - start))
        return result

    return wrapper


# region Download from Url - Not working
def dl_json(json_url):
    file_path = ''
    print('Downloading Json..' + json_url)

    try:
        response = requests.get(json_url)

        print('Status Code = {}'.format(response.status_code))

        if response.status_code == 200:
            file_name = gen_random_text() + '.json'
            # TODO: make not hardcode path
            path = '/Users/encetra/Work/uchy/docker-airflow/scripts/tmp/'
            file_path = path + file_name
            print('LOCAL FILE PATH = {}'.format(file_path))

            with open(file_path, 'wb') as fi:
                fi.write(response.content)

    except Exception as ex:
        print('Exception while downloading')
        print(str(ex))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
    finally:
        return file_path
# endregion


@timing
def process_file(filepath: str) -> list:
    result = []
    with open(filepath, 'r') as data:
        for line in data:
            value = line.strip()
            if value:
                # TODO: make an template for generate INSERT string using
                # format like: ['(v11, v12, v13)', ...] in right order.
                # It will make this function much faster.
                result.append(EventsLog(**json.loads(line.strip())))
    return result


@timing
def process_file_pd(filepath: str) -> pd.DataFrame:
    # Already checked that reading from file by pandas is slower,
    # But iteration may be faster, so we should check it.
    return pd.read_json(filepath, lines=True)


@timing
def write_to_db_log(data: list) -> None:
    # TODO: if `data` will be huge enough,
    #  we should make not a single query, but split it in a chunks
    #  and create and send query for each chunk in multiprocessing mode.
    db.insert(data)


@timing
def transfer_from_log_to_merge_tree(client) -> None:
    with open('sql/transfer_from_log_to_merge_tree.sql') as f:
        query = f.read()
        response = client.execute(query)
        print(response)


@timing
def drop_log_table(client) -> None:
    with open('sql/drop_log_table.sql') as f:
        query = f.read()
        response = client.execute(query)
        print(response)


if __name__ == "__main__":
    # TODO: Need use yandex api to provide opportunity to download from yandex
    # https://tech.yandex.com/disk/api/reference/content-docpage/
    # path = dl_json("https://yadi.sk/d/ARJShvDUgazjMQ")

    # TODO: create logger, and replace all "print"

    path = 'data/event-data.json'

    print('Start parsing: ')

    # TODO: check what faster:
    # pandas -> to huge str query
    # or
    # list -> to huge str query

    # result_df = process_file_pd(path)
    raws = process_file(path)

    print(f'Raws count: {len(raws)}')

    write_to_db_log(raws)

    # TODO: move connection from task to global and use config
    client = Client('localhost')

    transfer_from_log_to_merge_tree(client)
    drop_log_table(client)

