-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2017/ProductInstall.TXT

\copy usa_2017_product_install
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2017/ProductInstall_utf8.TXT'
WITH (FORMAT csv, HEADER true);