-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2022/TECHNOLOGY_LooKuP/TECHNOLOGY_LooKuP.TXT

\copy usa_2022_technology_lookup FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2022/TECHNOLOGY_LooKuP/TECHNOLOGY_LooKuP_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
