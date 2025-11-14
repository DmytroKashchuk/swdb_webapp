-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2022/SIC_LooKuP/SIC_LooKuP.TXT

\copy usa_2022_sic_loo_ku_p FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2022/SIC_LooKuP/SIC_LooKuP_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
