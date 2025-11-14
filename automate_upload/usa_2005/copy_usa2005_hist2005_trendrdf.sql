-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2005/Hist2005_trendrdf.txt

\copy usa_2005_hist2005_trendrdf FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2005/Hist2005_trendrdf_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
