-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2015/Hist2015_ENTERPRISE.txt

\copy europe_2015_hist2015_enterprise FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2015/Hist2015_ENTERPRISE_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
