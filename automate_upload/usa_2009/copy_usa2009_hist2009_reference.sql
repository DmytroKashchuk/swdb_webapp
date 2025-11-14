-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2009/Hist2009_reference.txt

\copy usa_2009_hist2009_reference FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2009/Hist2009_reference_utf8.txt' WITH (FORMAT csv, HEADER true);
