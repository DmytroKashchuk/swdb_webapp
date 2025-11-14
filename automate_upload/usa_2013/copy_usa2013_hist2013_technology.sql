-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2013/Hist2013_Technology.txt

\copy usa_2013_hist2013_technology
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2013/Hist2013_Technology_utf8.txt'
WITH (FORMAT csv, HEADER true);