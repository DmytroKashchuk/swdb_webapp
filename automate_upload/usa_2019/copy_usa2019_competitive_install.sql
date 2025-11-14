-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2019/CompetitiveInstall.TXT

\copy usa_2019_competitive_install
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2019/CompetitiveInstall_utf8.TXT'
WITH (FORMAT csv, HEADER true);