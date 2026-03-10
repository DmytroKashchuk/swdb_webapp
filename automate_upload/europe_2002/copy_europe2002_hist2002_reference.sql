-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2002/Hist2002_REFERENCE.txt

\copy europe_2002_hist2002_reference FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2002/Hist2002_REFERENCE_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
