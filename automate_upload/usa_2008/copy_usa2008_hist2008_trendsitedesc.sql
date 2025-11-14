-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2008/Hist2008_trendsitedesc.txt

\copy usa_2008_hist2008_trendsitedesc
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2008/Hist2008_trendsitedesc_utf8.txt'
WITH (FORMAT csv, HEADER true);