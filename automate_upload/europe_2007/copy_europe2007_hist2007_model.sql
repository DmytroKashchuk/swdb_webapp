-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2007/Hist2007_MODEL.txt

\copy europe_2007_hist2007_model FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2007/Hist2007_MODEL_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
