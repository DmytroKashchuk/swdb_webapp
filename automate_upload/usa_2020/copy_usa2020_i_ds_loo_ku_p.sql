-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2020_RDFv4.1/IDs_LooKuP/IDs_LooKuP.TXT

\copy usa_2020_i_ds_loo_ku_p
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2020_RDFv4.1/IDs_LooKuP/IDs_LooKuP_utf8.TXT'
WITH (FORMAT csv, HEADER true);