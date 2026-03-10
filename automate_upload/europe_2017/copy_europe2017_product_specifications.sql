-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2017/ProductSpecifications.TXT

\copy europe_2017_product_specifications FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2017/ProductSpecifications_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
