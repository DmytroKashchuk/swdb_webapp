-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_1997/Hist1997_SI2.txt

\copy usa_1997_hist1997_si2 FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_1997/Hist1997_SI2_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
