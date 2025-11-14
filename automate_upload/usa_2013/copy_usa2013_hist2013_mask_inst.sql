-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2013/Hist2013_MaskInst.txt

\copy usa_2013_hist2013_mask_inst
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2013/Hist2013_MaskInst_utf8.txt'
WITH (FORMAT csv, HEADER true);