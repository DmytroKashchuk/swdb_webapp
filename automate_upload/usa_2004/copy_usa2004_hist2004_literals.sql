-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2004/Hist2004_LITERALS.txt

\copy usa_2004_hist2004_literals
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2004/Hist2004_LITERALS_utf8.txt'
WITH (FORMAT csv, HEADER true);