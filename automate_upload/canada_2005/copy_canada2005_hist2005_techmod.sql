-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2005/Hist2005_TECHMOD.txt

\copy canada_2005_hist2005_techmod FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2005/Hist2005_TECHMOD_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
