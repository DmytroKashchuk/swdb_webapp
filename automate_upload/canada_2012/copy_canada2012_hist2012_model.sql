-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2012/Hist2012_MODEL.txt

\copy canada_2012_hist2012_model FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2012/Hist2012_MODEL_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
