-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2016/AdditionalEuropean.TXT

\copy usa_2016_additional_european FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2016/AdditionalEuropean_utf8.TXT' WITH (FORMAT csv, HEADER true);
