-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2007/Hist2007_literals.txt

\copy usa_2007_hist2007_literals FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_2007/Hist2007_literals_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
