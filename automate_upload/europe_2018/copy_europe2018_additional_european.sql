-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_aod_2018/AdditionalEuropean.TXT

\copy europe_2018_additional_european FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_aod_2018/AdditionalEuropean_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
