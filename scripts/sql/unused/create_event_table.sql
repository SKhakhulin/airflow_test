CREATE TABLE IF NOT EXISTS db_test.sql_events(
    ts DateTime,
    userId Nullable(UInt32),
    sessionId UInt32,
    page Nullable(FixedString(7)),
    auth UInt8,
    method FixedString(7),
    status UInt16,
    level Nullable(FixedString(4)),
    itemInSession UInt16,
    location Nullable(String),
    userAgent Nullable(String),
    lastName Nullable(FixedString(50)),
    firstName Nullable(FixedString(50)),
    registration DateTime,
    gender UInt8,
    artist Nullable(String),
    song Nullable(String),
    length Float32
 ) ENGINE = MergeTree()
        PARTITION BY (toYYYYMM(ts), method, status, gender)
        ORDER BY (intHash32(sessionId))