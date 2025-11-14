-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2009/Hist2009_dynamic.txt

\copy usa_2009_hist2009_dynamic FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2009/Hist2009_dynamic_utf8.txt' WITH (FORMAT csv, HEADER true);
