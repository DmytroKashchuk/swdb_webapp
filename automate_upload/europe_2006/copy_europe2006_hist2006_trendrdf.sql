-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2006/Hist2006_TRENDRDF.txt

\copy europe_2006_hist2006_trendrdf FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2006/Hist2006_TRENDRDF_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
