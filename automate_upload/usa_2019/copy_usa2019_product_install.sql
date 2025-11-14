-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2019/ProductInstall.TXT

\copy usa_2019_product_install
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2019/ProductInstall_utf8.TXT'
WITH (FORMAT csv, HEADER true);