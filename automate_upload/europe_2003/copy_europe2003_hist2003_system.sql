-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2003/Hist2003_SYSTEM.txt

\copy europe_2003_hist2003_system FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2003/Hist2003_SYSTEM_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
