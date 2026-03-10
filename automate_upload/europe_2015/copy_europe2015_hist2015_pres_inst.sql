-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2015/Hist2015_PresInst.txt

\copy europe_2015_hist2015_pres_inst FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2015/Hist2015_PresInst_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
