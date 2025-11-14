-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2006/Hist2006_corp.txt

\copy usa_2006_hist2006_corp FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2006/Hist2006_corp_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
