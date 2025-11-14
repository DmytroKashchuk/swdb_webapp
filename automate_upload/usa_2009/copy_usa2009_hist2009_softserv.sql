-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2009/Hist2009_softserv.txt

\copy usa_2009_hist2009_softserv FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2009/Hist2009_softserv_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
