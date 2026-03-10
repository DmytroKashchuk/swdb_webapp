-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2019/CompetitiveInstall.TXT

\copy canada_2019_competitive_install FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2019/CompetitiveInstall_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
