CREATE TABLE 'brand_feedbacks'
(
    'brand' String,
    'cabinet_id' String,
    'pos_feedbacks' JsonDocument,
    PRIMARY KEY ('brand', 'cabinet_id'),
);
