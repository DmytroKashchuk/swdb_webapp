-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2001/Hist2001_ADVECON.txt

\copy usa_2001_hist2001_advecon FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2001/Hist2001_ADVECON_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
