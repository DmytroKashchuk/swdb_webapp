-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2017/AdditionalEuropean.TXT

\copy usa_2017_additional_european FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2017/AdditionalEuropean_utf8.TXT' WITH (FORMAT csv, HEADER true);
