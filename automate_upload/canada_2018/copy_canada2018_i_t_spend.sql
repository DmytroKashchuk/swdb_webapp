-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_aod_2018/ITSpend.TXT

\copy canada_2018_i_t_spend FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_aod_2018/ITSpend_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
