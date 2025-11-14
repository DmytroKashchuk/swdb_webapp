-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2008/Hist2008_softserv.txt

\copy usa_2008_hist2008_softserv FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2008/Hist2008_softserv_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
