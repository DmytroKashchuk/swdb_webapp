-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2009/Hist2009_ADVECON.txt

\copy canada_2009_hist2009_advecon FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2009/Hist2009_ADVECON_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
