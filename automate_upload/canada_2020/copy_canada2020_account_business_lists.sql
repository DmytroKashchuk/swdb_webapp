-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_aod_2020_RDFv4.1/ACCOUNT_BUSINESS_LISTS/ACCOUNT_BUSINESS_LISTS.TXT

\copy canada_2020_account_business_lists FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_aod_2020_RDFv4.1/ACCOUNT_BUSINESS_LISTS/ACCOUNT_BUSINESS_LISTS_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
