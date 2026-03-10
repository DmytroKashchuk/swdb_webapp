-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/EMEA_aod_2021/SIC_LooKuP/SIC_LooKuP.TXT

\copy emea_2021_sic_loo_ku_p FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/EMEA_aod_2021/SIC_LooKuP/SIC_LooKuP_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
