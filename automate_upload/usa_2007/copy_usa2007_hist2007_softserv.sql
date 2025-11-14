-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2007/Hist2007_softserv.txt

\copy usa_2007_hist2007_softserv FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2007/Hist2007_softserv_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
