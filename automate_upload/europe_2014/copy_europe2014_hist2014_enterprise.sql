-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2014/Hist2014_ENTERPRISE.txt

\copy europe_2014_hist2014_enterprise FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2014/Hist2014_ENTERPRISE_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
