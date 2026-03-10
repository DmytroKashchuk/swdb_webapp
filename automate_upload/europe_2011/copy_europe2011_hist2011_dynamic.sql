-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2011/Hist2011_DYNAMIC.txt

\copy europe_2011_hist2011_dynamic FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2011/Hist2011_DYNAMIC_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
