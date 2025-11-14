-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_1999/Hist1999_TECHMOD.txt

\copy usa_1999_hist1999_techmod FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_1999/Hist1999_TECHMOD_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
