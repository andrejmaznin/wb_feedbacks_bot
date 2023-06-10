CREATE TABLE 'feedbacks'
(
    'id' String,
    'client_id' String,
    'barcode' String,
    'brands' JsonDocument,
    'created_at' Timestamp,
    'neg_feedback' String,
    'pos_feedback' String,
    PRIMARY KEY ('id')
);
