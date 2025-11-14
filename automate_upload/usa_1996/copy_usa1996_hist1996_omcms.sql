-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_1996/Hist1996_OMCMS.txt

\copy usa_1996_hist1996_omcms FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_1996/Hist1996_OMCMS_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
