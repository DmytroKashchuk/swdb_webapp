-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/APac_aod_2020_RDFv3.14/SiteLevelEnterprise.txt

\copy apac_2020_site_level_enterprise FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/APac_aod_2020_RDFv3.14/SiteLevelEnterprise_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER ',');
