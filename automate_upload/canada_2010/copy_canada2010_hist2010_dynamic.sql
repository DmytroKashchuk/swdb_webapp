-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2010/Hist2010_DYNAMIC.txt

\copy canada_2010_hist2010_dynamic FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2010/Hist2010_DYNAMIC_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
