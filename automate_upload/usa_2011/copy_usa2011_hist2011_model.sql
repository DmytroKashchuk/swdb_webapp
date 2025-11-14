-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2011/Hist2011_MODEL.txt

\copy usa_2011_hist2011_model
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2011/Hist2011_MODEL_utf8.txt'
WITH (FORMAT csv, HEADER true);