-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/EMEA_2019/BusinessInitiatives.TXT

\copy emea_2019_business_initiatives FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/EMEA_2019/BusinessInitiatives_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
