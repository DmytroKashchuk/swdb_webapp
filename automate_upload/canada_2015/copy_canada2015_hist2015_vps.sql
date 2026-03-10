-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2015/Hist2015_VPS.txt

\copy canada_2015_hist2015_vps FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2015/Hist2015_VPS_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
