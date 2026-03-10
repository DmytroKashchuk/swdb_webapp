-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2000/Hist2000_SITEDESC.txt

\copy canada_2000_hist2000_sitedesc FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2000/Hist2000_SITEDESC_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
