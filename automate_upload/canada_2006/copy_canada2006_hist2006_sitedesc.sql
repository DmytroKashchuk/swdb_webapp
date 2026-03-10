-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2006/Hist2006_SITEDESC.txt

\copy canada_2006_hist2006_sitedesc FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2006/Hist2006_SITEDESC_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
