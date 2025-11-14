-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2009/Hist2009_techmod.txt

\copy usa_2009_hist2009_techmod FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2009/Hist2009_techmod_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
