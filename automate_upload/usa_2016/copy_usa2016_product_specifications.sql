-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2016/ProductSpecifications.TXT

\copy usa_2016_product_specifications
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2016/ProductSpecifications_utf8.TXT'
WITH (FORMAT csv, HEADER true);