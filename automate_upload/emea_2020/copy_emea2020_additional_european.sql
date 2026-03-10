-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/EMEA_aod_2020_RDFv3.14/AdditionalEuropean.TXT

\copy emea_2020_additional_european FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/EMEA_aod_2020_RDFv3.14/AdditionalEuropean_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
