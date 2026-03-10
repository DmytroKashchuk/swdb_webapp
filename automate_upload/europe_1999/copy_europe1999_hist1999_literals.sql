-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_1999/Hist1999_LITERALS.txt

\copy europe_1999_hist1999_literals FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/Europe_1999/Hist1999_LITERALS_utf8.txt' WITH (FORMAT csv, HEADER true, DELIMITER E'\t');
