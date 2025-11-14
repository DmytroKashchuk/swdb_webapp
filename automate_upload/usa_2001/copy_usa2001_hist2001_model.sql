-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2001/Hist2001_MODEL.txt

\copy usa_2001_hist2001_model FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2001/Hist2001_MODEL_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
