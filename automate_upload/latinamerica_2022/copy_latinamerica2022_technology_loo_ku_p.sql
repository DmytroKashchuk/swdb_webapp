-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_aod_2022/TECHNOLOGY_LooKuP/TECHNOLOGY_LooKuP.TXT

\copy latinamerica_2022_technology_loo_ku_p FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_aod_2022/TECHNOLOGY_LooKuP/TECHNOLOGY_LooKuP_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
