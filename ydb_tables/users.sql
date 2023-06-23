CREATE TABLE `users`
(
    `id` String,
    `client_id` String,
    `data` String,
    `owner` Bool,
    `pending` Bool,
    `telegram_id` String,
    `username` String,
    PRIMARY KEY (`id`)
);
