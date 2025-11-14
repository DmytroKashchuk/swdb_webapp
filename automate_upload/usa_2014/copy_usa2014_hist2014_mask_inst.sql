-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2014/Hist2014_MaskInst.txt

\copy usa_2014_hist2014_mask_inst
FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2014/Hist2014_MaskInst_utf8.txt'
WITH (FORMAT csv, HEADER true);