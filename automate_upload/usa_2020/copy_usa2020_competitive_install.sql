-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2020_RDFv3.14/CompetitiveInstall.TXT

\copy usa_2020_competitive_install
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2020_RDFv3.14/CompetitiveInstall_utf8.TXT'
WITH (FORMAT csv, HEADER true);