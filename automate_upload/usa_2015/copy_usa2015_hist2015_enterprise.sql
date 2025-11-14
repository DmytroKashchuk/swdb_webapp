-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2015/Hist2015_ENTERPRISE.txt

\copy usa_2015_hist2015_enterprise FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2015/Hist2015_ENTERPRISE_utf8.txt' WITH (FORMAT csv, HEADER true);
