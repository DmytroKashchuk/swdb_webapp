-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2004/Hist2004_CORP.txt

\copy usa_2004_hist2004_corp
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2004/Hist2004_CORP_utf8.txt'
WITH (FORMAT csv, HEADER true);