-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2016/PresenceInstall.TXT

\copy usa_2016_presence_install
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2016/PresenceInstall_utf8.TXT'
WITH (FORMAT csv, HEADER true);