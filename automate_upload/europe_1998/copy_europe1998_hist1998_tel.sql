-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_1998/Hist1998_TEL.txt

\copy europe_1998_hist1998_tel FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_1998/Hist1998_TEL_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
