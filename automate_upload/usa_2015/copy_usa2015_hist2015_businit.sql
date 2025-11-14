-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2015/Hist2015_BUSINIT.txt

\copy usa_2015_hist2015_businit FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2015/Hist2015_BUSINIT_utf8.txt' WITH (FORMAT csv, HEADER true);
