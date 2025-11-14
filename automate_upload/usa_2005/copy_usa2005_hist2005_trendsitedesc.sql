-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2005/Hist2005_trendsitedesc.txt

\copy usa_2005_hist2005_trendsitedesc
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2005/Hist2005_trendsitedesc_utf8.txt'
WITH (FORMAT csv, HEADER true);