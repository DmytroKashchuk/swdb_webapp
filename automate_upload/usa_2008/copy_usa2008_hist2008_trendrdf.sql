-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2008/Hist2008_trendrdf.txt

\copy usa_2008_hist2008_trendrdf FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2008/Hist2008_trendrdf_utf8.txt' WITH (FORMAT csv, HEADER true);
