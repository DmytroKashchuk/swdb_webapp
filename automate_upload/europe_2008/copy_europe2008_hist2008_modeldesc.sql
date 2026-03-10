-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2008/Hist2008_MODELDESC.txt

\copy europe_2008_hist2008_modeldesc FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2008/Hist2008_MODELDESC_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
