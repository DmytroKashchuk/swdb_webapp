-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2010/Hist2010_PLS.txt

\copy usa_2010_hist2010_pls
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2010/Hist2010_PLS_utf8.txt'
WITH (FORMAT csv, HEADER true);