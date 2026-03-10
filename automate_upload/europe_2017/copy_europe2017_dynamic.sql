-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2017/Dynamic.TXT

\copy europe_2017_dynamic FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2017/Dynamic_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
