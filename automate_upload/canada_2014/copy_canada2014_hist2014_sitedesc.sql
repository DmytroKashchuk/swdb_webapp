-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2014/Hist2014_Sitedesc.txt

\copy canada_2014_hist2014_sitedesc FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2014/Hist2014_Sitedesc_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
