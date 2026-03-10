-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_1997/Hist1997_SI2.txt

\copy europe_1997_hist1997_si2 FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_1997/Hist1997_SI2_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
