-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2019/Dynamic.TXT

\copy usa_2019_dynamic
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2019/Dynamic_utf8.TXT'
WITH (FORMAT csv, HEADER true);