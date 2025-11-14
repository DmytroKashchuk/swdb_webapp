-- load data for: /home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2020_RDFv3.14/ITSpend.txt

\copy usa_2020_i_t_spend FROM '/home/dima/swdb/swdb_all_data/swdb_all_data_unziped/USA_aod_2020_RDFv3.14/ITSpend_utf8.txt' WITH (FORMAT csv, HEADER true);
