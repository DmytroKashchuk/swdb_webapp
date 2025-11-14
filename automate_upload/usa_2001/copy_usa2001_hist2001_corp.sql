-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2001/Hist2001_CORP.txt

\copy usa_2001_hist2001_corp FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2001/Hist2001_CORP_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
