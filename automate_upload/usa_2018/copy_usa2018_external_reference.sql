-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2018/ExternalReference.TXT

\copy usa_2018_external_reference FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2018/ExternalReference_utf8.TXT' WITH (FORMAT csv, HEADER true);
