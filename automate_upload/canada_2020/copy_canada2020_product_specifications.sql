-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_aod_2020_RDFv3.14/ProductSpecifications.TXT

\copy canada_2020_product_specifications FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_aod_2020_RDFv3.14/ProductSpecifications_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
