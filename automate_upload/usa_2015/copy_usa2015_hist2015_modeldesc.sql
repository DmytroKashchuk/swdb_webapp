-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2015/Hist2015_MODELDESC.txt

\copy usa_2015_hist2015_modeldesc FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2015/Hist2015_MODELDESC_utf8.txt' WITH (FORMAT csv, HEADER true);
