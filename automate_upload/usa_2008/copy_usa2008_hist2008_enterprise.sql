-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2008/Hist2008_enterprise.txt

\copy usa_2008_hist2008_enterprise
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2008/Hist2008_enterprise_utf8.txt'
WITH (FORMAT csv, HEADER true);