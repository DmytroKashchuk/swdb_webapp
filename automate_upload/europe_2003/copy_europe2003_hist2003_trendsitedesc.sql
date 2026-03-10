-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2003/Hist2003_TRENDSITEDESC.txt

\copy europe_2003_hist2003_trendsitedesc FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2003/Hist2003_TRENDSITEDESC_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
