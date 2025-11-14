-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2018/BusinessInitiatives.TXT

\copy usa_2018_business_initiatives FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2018/BusinessInitiatives_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
