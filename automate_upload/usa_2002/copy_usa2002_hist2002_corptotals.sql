-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2002/Hist2002_CORPTOTALS.txt

\copy usa_2002_hist2002_corptotals
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2002/Hist2002_CORPTOTALS_utf8.txt'
WITH (FORMAT csv, HEADER true);