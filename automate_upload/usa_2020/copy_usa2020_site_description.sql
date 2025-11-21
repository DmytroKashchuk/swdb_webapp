-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2020_RDFv3.14/SiteDescription.TXT

\copy usa_2020_site_description FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2020/SiteDescription_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
