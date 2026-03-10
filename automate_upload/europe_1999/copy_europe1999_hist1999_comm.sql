-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_1999/Hist1999_COMM.txt

\copy europe_1999_hist1999_comm FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_1999/Hist1999_COMM_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
