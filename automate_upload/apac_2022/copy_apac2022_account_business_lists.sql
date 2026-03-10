-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/APac_aod_2022/ACCOUNT_BUSINESS_LISTS/ACCOUNT_BUSINESS_LISTS.TXT

\copy apac_2022_account_business_lists FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/APac_aod_2022/ACCOUNT_BUSINESS_LISTS/ACCOUNT_BUSINESS_LISTS_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
