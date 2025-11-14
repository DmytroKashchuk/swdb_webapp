-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2002/Hist2002_TECHMOD_BASE.txt

\copy usa_2002_hist2002_techmod_base FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2002/Hist2002_TECHMOD_BASE_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
