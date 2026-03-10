-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/APac_aod_2020_RDFv4.1/SITES_TECHNOLOGY/SITES_TECHNOLOGY.TXT

\copy apac_2020_sites_technology FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/APac_aod_2020_RDFv4.1/SITES_TECHNOLOGY/SITES_TECHNOLOGY_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
