-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2021/NAICS_LooKuP/NAICS_LooKuP.TXT

\copy usa_2021_naics_loo_ku_p FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2021/NAICS_LooKuP/NAICS_LooKuP_utf8.TXT' WITH (FORMAT csv, HEADER true);
