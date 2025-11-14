-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2017/TechnologyTotals.TXT

\copy usa_2017_technology_totals FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2017/TechnologyTotals_utf8.TXT' WITH (FORMAT csv, HEADER true);
