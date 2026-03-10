-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2003/Hist2003_TRENDSYSTEM.txt

\copy canada_2003_hist2003_trendsystem FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2003/Hist2003_TRENDSYSTEM_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
