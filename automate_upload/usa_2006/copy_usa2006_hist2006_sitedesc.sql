-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2006/Hist2006_sitedesc.txt

\copy usa_2006_hist2006_sitedesc
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2006/Hist2006_sitedesc_utf8.txt'
WITH (FORMAT csv, HEADER true);