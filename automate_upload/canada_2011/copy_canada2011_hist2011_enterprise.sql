-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2011/Hist2011_ENTERPRISE.txt

\copy canada_2011_hist2011_enterprise FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2011/Hist2011_ENTERPRISE_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
