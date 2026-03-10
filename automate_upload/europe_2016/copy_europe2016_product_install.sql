-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2016/ProductInstall.TXT

\copy europe_2016_product_install FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2016/ProductInstall_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
