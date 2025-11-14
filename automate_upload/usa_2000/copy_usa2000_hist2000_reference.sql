-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2000/Hist2000_REFERENCE.txt

\copy usa_2000_hist2000_reference
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2000/Hist2000_REFERENCE_utf8.txt'
WITH (FORMAT csv, HEADER true);