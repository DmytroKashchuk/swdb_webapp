-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_aod_2018/AdditionalEuropean.TXT

\copy canada_2018_additional_european FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_aod_2018/AdditionalEuropean_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
