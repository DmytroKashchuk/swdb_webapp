-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2004/Hist2004_MODEL.txt

\copy canada_2004_hist2004_model FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2004/Hist2004_MODEL_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
