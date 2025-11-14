-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2011/Hist2011_DYNAMIC.txt

\copy usa_2011_hist2011_dynamic
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2011/Hist2011_DYNAMIC_utf8.txt'
WITH (FORMAT csv, HEADER true);