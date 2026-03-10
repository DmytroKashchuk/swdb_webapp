-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2017/ExternalReference.TXT

\copy europe_2017_external_reference FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2017/ExternalReference_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
