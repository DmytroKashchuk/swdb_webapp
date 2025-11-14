-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2015/Hist2015_MaskInst.txt

\copy usa_2015_hist2015_mask_inst FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2015/Hist2015_MaskInst_utf8.txt' WITH (FORMAT csv, HEADER true);
