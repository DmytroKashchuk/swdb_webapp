-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_1997/Hist1997_OMCMS.txt

\copy usa_1997_hist1997_omcms FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_1997/Hist1997_OMCMS_utf8.txt' WITH (FORMAT csv, HEADER true);
