-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2003/Hist2003_DYNAMIC.txt

\copy usa_2003_hist2003_dynamic
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2003/Hist2003_DYNAMIC_utf8.txt'
WITH (FORMAT csv, HEADER true);