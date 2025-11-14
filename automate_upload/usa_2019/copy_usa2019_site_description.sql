-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2019/SiteDescription.TXT

\copy usa_2019_site_description FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2019/SiteDescription_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
