CREATE TABLE 'barcode_feedbacks'
(
    'barcode' String,
    'cabinet_id' String,
    'pos_feedback' String,
    PRIMARY KEY (`barcode`, 'cabinet_id')
);
