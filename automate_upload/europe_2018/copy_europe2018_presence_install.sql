-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_aod_2018/PresenceInstall.TXT

\copy europe_2018_presence_install FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_aod_2018/PresenceInstall_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
