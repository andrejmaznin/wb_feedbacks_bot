CREATE TABLE 'commands'
(
    'id' String,
    'client_id' String,
    'command' String,
    'created_at' Timestamp,
    'metadata' JsonDocument,
    'parent' String,
    'telegram_id' String,
    PRIMARY KEY ('id'),
);
