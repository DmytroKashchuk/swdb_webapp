-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/EMEA_2019/ProductSpecifications.TXT

\copy emea_2019_product_specifications FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/EMEA_2019/ProductSpecifications_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
