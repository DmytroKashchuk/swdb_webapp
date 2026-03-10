-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_aod_2018/PresenceInstall.TXT

\copy canada_2018_presence_install FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_aod_2018/PresenceInstall_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
