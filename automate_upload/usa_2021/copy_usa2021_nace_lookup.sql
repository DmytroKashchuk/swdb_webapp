-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2021/NACE_LooKuP/NACE_LooKuP.TXT

\copy usa_2021_nace_lookup FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2021/NACE_LooKuP/NACE_LooKuP_utf8.TXT' WITH (FORMAT csv, HEADER true, DELIMITER ',');
