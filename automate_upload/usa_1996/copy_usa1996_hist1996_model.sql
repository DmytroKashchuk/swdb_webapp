-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_1996/Hist1996_MODEL.txt

\copy usa_1996_hist1996_model
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_1996/Hist1996_MODEL_utf8.txt'
WITH (FORMAT csv, HEADER true);