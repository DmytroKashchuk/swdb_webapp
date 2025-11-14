-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2012/Hist2012_DYNAMIC.txt

\copy usa_2012_hist2012_dynamic FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2012/Hist2012_DYNAMIC_utf8.txt' WITH (FORMAT csv, HEADER true);
