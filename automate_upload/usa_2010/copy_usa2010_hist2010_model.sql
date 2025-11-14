-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2010/Hist2010_MODEL.txt

\copy usa_2010_hist2010_model FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2010/Hist2010_MODEL_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
