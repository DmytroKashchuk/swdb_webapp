-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2001/Hist2001_MODELDESC.txt

\copy usa_2001_hist2001_modeldesc
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2001/Hist2001_MODELDESC_utf8.txt'
WITH (FORMAT csv, HEADER true);