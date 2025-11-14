-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2013/Hist2013_DYNAMIC.txt

\copy usa_2013_hist2013_dynamic
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2013/Hist2013_DYNAMIC_utf8.txt'
WITH (FORMAT csv, HEADER true);