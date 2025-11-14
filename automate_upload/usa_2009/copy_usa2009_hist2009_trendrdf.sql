-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2009/Hist2009_trendrdf.txt

\copy usa_2009_hist2009_trendrdf
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2009/Hist2009_trendrdf_utf8.txt'
WITH (FORMAT csv, HEADER true);