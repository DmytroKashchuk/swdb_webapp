-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2019/Dynamic.TXT

\copy canada_2019_dynamic FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2019/Dynamic_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
