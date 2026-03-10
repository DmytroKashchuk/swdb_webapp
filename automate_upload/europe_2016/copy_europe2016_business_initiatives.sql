-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2016/BusinessInitiatives.TXT

\copy europe_2016_business_initiatives FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2016/BusinessInitiatives_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
