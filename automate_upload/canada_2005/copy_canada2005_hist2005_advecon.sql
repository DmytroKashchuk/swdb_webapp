-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2005/Hist2005_ADVECON.txt

\copy canada_2005_hist2005_advecon FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2005/Hist2005_ADVECON_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
