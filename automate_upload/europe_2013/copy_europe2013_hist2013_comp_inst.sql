-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2013/Hist2013_CompInst.txt

\copy europe_2013_hist2013_comp_inst FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_2013/Hist2013_CompInst_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
