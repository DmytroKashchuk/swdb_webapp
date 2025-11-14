-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_1997/Hist1997_MODEL.txt

\copy usa_1997_hist1997_model FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_1997/Hist1997_MODEL_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
