-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2002/Hist2002_CORP.txt

\copy europe_2002_hist2002_corp FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2002/Hist2002_CORP_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
