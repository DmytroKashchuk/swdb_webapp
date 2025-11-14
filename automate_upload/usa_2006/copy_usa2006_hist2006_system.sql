-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2006/Hist2006_system.txt

\copy usa_2006_hist2006_system FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2006/Hist2006_system_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
