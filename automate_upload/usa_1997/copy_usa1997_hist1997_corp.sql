-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_1997/Hist1997_CORP.txt

\copy usa_1997_hist1997_corp
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_1997/Hist1997_CORP_utf8.txt'
WITH (FORMAT csv, HEADER true);