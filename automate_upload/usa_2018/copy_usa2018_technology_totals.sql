-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2018/TechnologyTotals.TXT

\copy usa_2018_technology_totals
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2018/TechnologyTotals_utf8.TXT'
WITH (FORMAT csv, HEADER true);