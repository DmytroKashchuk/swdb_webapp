-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2010/Hist2010_BUSINIT.txt

\copy usa_2010_hist2010_businit
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2010/Hist2010_BUSINIT_utf8.txt'
WITH (FORMAT csv, HEADER true);