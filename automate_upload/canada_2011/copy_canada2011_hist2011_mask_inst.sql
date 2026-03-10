-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2011/Hist2011_MaskInst.txt

\copy canada_2011_hist2011_mask_inst FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Canada_2011/Hist2011_MaskInst_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
