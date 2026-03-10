-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2004/Hist2004_EBUSINESS.txt

\copy canada_2004_hist2004_ebusiness FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2004/Hist2004_EBUSINESS_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
