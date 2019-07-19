from infi.clickhouse_orm.database import Database
from infi.clickhouse_orm.models import Model
from infi.clickhouse_orm.fields import *
from infi.clickhouse_orm.engines import MergeTree, Log
from enum import Enum


class Level(Enum):
    free = 0
    paid = 1


class Gender(Enum):
    U = 0
    M = 1
    F = 2


class Events(Model):
    ts = DateTimeField()
    userId = UInt32Field()
    sessionId = UInt32Field()
    page = FixedStringField(50)
    auth = FixedStringField(10)
    method = FixedStringField(7)
    status = UInt16Field()
    level = Enum8Field(Level)
    itemInSession = UInt16Field()
    location = NullableField(StringField())
    userAgent = NullableField(StringField())
    lastName = NullableField(FixedStringField(50))
    firstName = NullableField(FixedStringField(50))
    registration = DateTimeField()
    gender = Enum8Field(Gender)
    artist = NullableField(StringField())
    song = NullableField(StringField())
    length = Float32Field()

    engine = MergeTree(
        partition_key=('auth', ),
        order_by=('userId', 'ts', 'page', 'gender',),
    )


class EventsLog(Model):

    ts = UInt64Field()
    userId = StringField()
    sessionId = UInt32Field()
    page = StringField()
    auth = StringField()
    method = NullableField(StringField())
    status = NullableField(UInt16Field())
    level = StringField()
    itemInSession = NullableField(UInt16Field())
    location = NullableField(StringField())
    userAgent = NullableField(StringField())
    lastName = NullableField(StringField())
    firstName = NullableField(StringField())
    registration = UInt64Field()
    gender = NullableField(StringField())
    artist = NullableField(StringField())
    song = NullableField(StringField())
    length = NullableField(Float32Field())

    engine = Log()


db = Database('db_test', db_url='http://clickhouse:8123')

db.create_table(Events)
db.create_table(EventsLog)
