-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2005/Hist2005_modeldesc.txt

\copy usa_2005_hist2005_modeldesc FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2005/Hist2005_modeldesc_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
