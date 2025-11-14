-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2013/Hist2013_ILS.txt

\copy usa_2013_hist2013_ils
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2013/Hist2013_ILS_utf8.txt'
WITH (FORMAT csv, HEADER true);