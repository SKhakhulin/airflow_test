import os
import sys
import uuid
import json
import requests

from airflow import DAG
from clickhouse_driver import Client
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator

from models import db, EventsLog

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime.now(),
    "email": ["email@email.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


# region Unused part for download from external source by url
def gen_random_text():
    return uuid.uuid4().hex


def dl_json(json_url):
    file_name = ''
    print('Downloading Json..' + json_url)

    try:
        response = requests.get(json_url)

        print('Status Code = {}'.format(response.status_code))

        if response.status_code == 200:
            file_name = gen_random_text() + '.json'
            path = '/usr/local/airflow/tmp/'
            file_path = path + file_name
            print('LOCAL FILE PATH = {}'.format(file_path))

    except Exception as ex:
        print('Exception while downloading')
        print(str(ex))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        file_name = None
    finally:
        return file_name


def download_json(**kwargs):
    # TODO: make it work with Yandex api
    #       use url from Airflow Variables
    return dl_json(json_url='')
# endregion

# region Plugin part
# TODO: move to plugin


# region Load Json
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


def write_to_db_log(data: list) -> None:
    # TODO: if `data` will be huge enough,
    #  we should make not a single query, but split it in a chunks
    #  and create and send query for each chunk in multiprocessing mode.
    db.insert(data)


def load_json(**kwargs):
    path = '/usr/local/airflow/data/event-data.json'
    raws = process_file(path)
    write_to_db_log(raws)
# endregion


# region Move to Merge tree
def transfer_from_log_to_merge_tree(client) -> None:
    with open('/usr/local/airflow/dags/sql/transfer_from_log_to_merge_tree.sql') as f:
        query = f.read()
        response = client.execute(query)
        print(response)


def drop_log_table(client) -> None:
    with open('/usr/local/airflow/dags/sql/drop_log_table.sql') as f:
        query = f.read()
        response = client.execute(query)
        print(response)


def move_to_merge_tree(**kwargs):
    client = Client('clickhouse')
    transfer_from_log_to_merge_tree(client)
    drop_log_table(client)

# endregion
# endregion


with DAG(
        dag_id='website_statistics',
        default_args=default_args,
        schedule_interval=timedelta(minutes=1)) as dag:

    # Task for download from external source
    # opr_download_json = PythonOperator(task_id='download_json', python_callable=download_json, provide_context=True)

    opr_extract_json = PythonOperator(
        task_id='load_json',
        provide_context=True,
        python_callable=load_json,
    )

    opr_transform_clickhouse = PythonOperator(
        task_id='move_to_merge_tree',
        provide_context=True,
        python_callable=move_to_merge_tree,
    )

    # opr_extract_json.set_downstream(opr_download_json)
    opr_extract_json.set_downstream(opr_transform_clickhouse)

    # opr_transform_clickhouse.set_downstream(opr_extract_json)

