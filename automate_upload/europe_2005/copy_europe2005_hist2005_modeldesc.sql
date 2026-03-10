-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2005/Hist2005_MODELDESC.txt

\copy europe_2005_hist2005_modeldesc FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2005/Hist2005_MODELDESC_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
