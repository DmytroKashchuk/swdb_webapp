-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/EMEA_aod_2020_RDFv3.14/ITSpend.txt

\copy emea_2020_i_t_spend FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/EMEA_aod_2020_RDFv3.14/ITSpend_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER ',');
