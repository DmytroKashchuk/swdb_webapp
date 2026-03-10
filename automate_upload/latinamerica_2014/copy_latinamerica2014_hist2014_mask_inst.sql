-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2014/Hist2014_MaskInst.txt

\copy latinamerica_2014_hist2014_mask_inst FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/LatinAmerica_2014/Hist2014_MaskInst_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
