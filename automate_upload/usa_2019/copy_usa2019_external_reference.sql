-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2019/ExternalReference.TXT

\copy usa_2019_external_reference
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2019/ExternalReference_utf8.TXT'
WITH (FORMAT csv, HEADER true);