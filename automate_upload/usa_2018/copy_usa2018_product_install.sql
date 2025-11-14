-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2018/ProductInstall.TXT

\copy usa_2018_product_install FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2018/ProductInstall_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
