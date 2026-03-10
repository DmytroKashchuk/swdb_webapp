-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2018/ExternalReference.TXT

\copy canada_2018_external_reference FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2018/ExternalReference_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
