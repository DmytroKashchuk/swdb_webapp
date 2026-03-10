-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2001/Hist2001_SITEDESC.txt

\copy canada_2001_hist2001_sitedesc FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2001/Hist2001_SITEDESC_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
