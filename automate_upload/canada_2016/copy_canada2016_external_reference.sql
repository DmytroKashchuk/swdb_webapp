-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2016/ExternalReference.TXT

\copy canada_2016_external_reference FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2016/ExternalReference_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
