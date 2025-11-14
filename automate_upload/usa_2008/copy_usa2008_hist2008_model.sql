-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2008/Hist2008_model.txt

\copy usa_2008_hist2008_model FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2008/Hist2008_model_utf8.txt' WITH (FORMAT csv, HEADER true);
