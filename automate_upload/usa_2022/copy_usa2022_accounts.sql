-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2022/ACCOUNTS/ACCOUNTS.TXT

\copy usa_2022_accounts
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2022/ACCOUNTS/ACCOUNTS_utf8.TXT'
WITH (FORMAT csv, HEADER true);