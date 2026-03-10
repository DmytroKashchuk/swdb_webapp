-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2019/ProductInstall.TXT

\copy latinamerica_2019_product_install FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2019/ProductInstall_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
