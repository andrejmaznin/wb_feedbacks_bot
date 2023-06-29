CREATE TABLE `admin_credentials`
(
    `id`               String,
    `created_at`       Timestamp,
    `ms_access_token`  String,
    `ms_refresh_token` String,
    PRIMARY KEY (`id`)
);
