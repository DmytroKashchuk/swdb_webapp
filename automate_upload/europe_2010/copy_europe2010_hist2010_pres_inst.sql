-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2010/Hist2010_PresInst.txt

\copy europe_2010_hist2010_pres_inst FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2010/Hist2010_PresInst_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
