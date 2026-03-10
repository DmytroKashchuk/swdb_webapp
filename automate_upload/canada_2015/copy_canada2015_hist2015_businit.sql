-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2015/Hist2015_BUSINIT.txt

\copy canada_2015_hist2015_businit FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2015/Hist2015_BUSINIT_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
