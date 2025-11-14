-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2021/SITES_TECHNOLOGY/SITES_TECHNOLOGY.TXT

\copy usa_2021_sites_technology FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2021/SITES_TECHNOLOGY/SITES_TECHNOLOGY_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
