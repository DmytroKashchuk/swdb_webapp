-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_1998/Hist1998_NET.txt

\copy europe_1998_hist1998_net FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_1998/Hist1998_NET_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
