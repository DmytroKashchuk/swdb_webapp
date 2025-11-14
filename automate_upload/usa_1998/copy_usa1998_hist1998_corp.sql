-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_1998/Hist1998_CORP.txt

\copy usa_1998_hist1998_corp
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_1998/Hist1998_CORP_utf8.txt'
WITH (FORMAT csv, HEADER true);