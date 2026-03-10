-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_aod_2021/NACE_LooKuP/NACE_LooKuP.TXT

\copy latinamerica_2021_nace_loo_ku_p FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_aod_2021/NACE_LooKuP/NACE_LooKuP_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
