-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/EMEA_aod_2021/ACCOUNTS/ACCOUNTS.TXT

\copy emea_2021_accounts FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/EMEA_aod_2021/ACCOUNTS/ACCOUNTS_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
