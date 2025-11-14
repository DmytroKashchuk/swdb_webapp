-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2016/Dynamic.TXT

\copy usa_2016_dynamic FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2016/Dynamic_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
