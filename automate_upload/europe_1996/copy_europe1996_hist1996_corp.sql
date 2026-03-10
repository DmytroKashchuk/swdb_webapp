-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_1996/Hist1996_CORP.txt

\copy europe_1996_hist1996_corp FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_1996/Hist1996_CORP_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
