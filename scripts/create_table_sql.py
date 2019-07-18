# Unused file because of using ORM
# Left it here to show that I understand
# how to create DB and Tables by SQL

from clickhouse_driver import Client


def create_table(client):

    with open('sql/old/create_test_database.sql') as f:
        query = f.read()
        result = client.execute(query)

    with open('sql/old/create_event_table.sql') as f:
        query = f.read()
        result = client.execute(query)

    with open('sql/old/create_event_log_table.sql') as f:
        query = f.read()
        result = client.execute(query)


if __name__ == "__main__":
    client = Client('localhost')
    create_table(client)
