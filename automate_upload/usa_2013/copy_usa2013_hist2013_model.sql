-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2013/Hist2013_MODEL.txt

\copy usa_2013_hist2013_model FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2013/Hist2013_MODEL_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
