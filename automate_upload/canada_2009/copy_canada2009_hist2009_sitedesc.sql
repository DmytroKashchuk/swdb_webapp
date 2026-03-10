-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2009/Hist2009_SITEDESC.txt

\copy canada_2009_hist2009_sitedesc FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2009/Hist2009_SITEDESC_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
