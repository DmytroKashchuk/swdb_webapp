-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2002/Hist2002_ADVECON.txt

\copy usa_2002_hist2002_advecon
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2002/Hist2002_ADVECON_utf8.txt'
WITH (FORMAT csv, HEADER true);